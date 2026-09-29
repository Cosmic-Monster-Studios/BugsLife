package com.bugslife.entity;

import com.bugslife.bug.BugData;
import com.bugslife.bug.BugRarity;
import com.bugslife.bug.BugSpecies;
import com.bugslife.bug.Movement;
import com.bugslife.entity.goal.BugFlyGoal;
import com.bugslife.entity.goal.BugPanicGoal;
import com.bugslife.entity.goal.ClingGoal;
import com.bugslife.entity.goal.FlowerVisitGoal;
import com.bugslife.entity.goal.FollowLivestockGoal;
import com.bugslife.entity.goal.HuntAphidGoal;
import com.bugslife.entity.goal.LightOrbitGoal;
import com.bugslife.entity.goal.RestGoal;
import com.bugslife.entity.goal.SparGoal;
import com.bugslife.registry.ModEntities;
import com.bugslife.registry.ModItems;
import com.bugslife.registry.ModTriggers;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.particles.ColorParticleOption;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.syncher.EntityDataAccessor;
import net.minecraft.network.syncher.EntityDataSerializers;
import net.minecraft.network.syncher.SynchedEntityData;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.Mth;
import net.minecraft.world.DifficultyInstance;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.entity.AgeableMob;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.SpawnGroupData;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.control.FlyingMoveControl;
import net.minecraft.world.entity.ai.goal.AvoidEntityGoal;
import net.minecraft.world.entity.ai.goal.BreedGoal;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.ai.goal.RandomStrollGoal;
import net.minecraft.world.entity.ai.goal.TemptGoal;
import net.minecraft.world.entity.ai.goal.WaterAvoidingRandomStrollGoal;
import net.minecraft.world.entity.ai.navigation.FlyingPathNavigation;
import net.minecraft.world.entity.ai.navigation.GroundPathNavigation;
import net.minecraft.world.entity.ai.navigation.PathNavigation;
import net.minecraft.world.entity.ai.navigation.WallClimberNavigation;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.ServerLevelAccessor;
import net.minecraft.world.level.block.LiquidBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.material.FluidState;
import net.minecraft.world.level.pathfinder.PathFinder;
import net.minecraft.world.level.pathfinder.PathType;
import net.minecraft.world.level.pathfinder.WalkNodeEvaluator;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.CollisionContext;
import org.jetbrains.annotations.Nullable;
import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.animation.AnimatableManager;
import software.bernie.geckolib.animation.AnimationController;
import software.bernie.geckolib.animation.AnimationState;
import software.bernie.geckolib.animation.PlayState;
import software.bernie.geckolib.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

import java.util.EnumMap;
import java.util.Map;
import java.util.function.Predicate;
import net.minecraft.world.level.block.Blocks;

/**
 * Every bug is one of these. Behaviour is chosen from its {@link BugSpecies}: how it moves, which goals it runs,
 * and its special tricks (rolling up, freezing when watched, sensing footsteps, teleporting...).
 */
public class BugEntity extends Animal implements GeoEntity {
    private static final EntityDataAccessor<Byte> DATA_FLAGS = SynchedEntityData.defineId(BugEntity.class, EntityDataSerializers.BYTE);
    private static final EntityDataAccessor<Boolean> DATA_PRISMATIC = SynchedEntityData.defineId(BugEntity.class, EntityDataSerializers.BOOLEAN);
    private static final EntityDataAccessor<Float> DATA_SIZE = SynchedEntityData.defineId(BugEntity.class, EntityDataSerializers.FLOAT);
    private static final EntityDataAccessor<Byte> DATA_CLING = SynchedEntityData.defineId(BugEntity.class, EntityDataSerializers.BYTE);

    public static final int FLAG_CLIMBING = 1;
    public static final int FLAG_ROLLED = 2;
    public static final int FLAG_ALERT = 4;
    public static final int FLAG_FROZEN = 8;
    public static final int FLAG_PERCHED = 16;
    /** Buried (antlion) or underground (mole cricket). */
    public static final int FLAG_HIDDEN = 32;

    /** 1 in this many wild bugs is prismatic. */
    public static final int WILD_PRISMATIC_CHANCE = 400;

    private final AnimatableInstanceCache geoCache = GeckoLibUtil.createInstanceCache(this);
    private BugSpecies speciesCache;

    private boolean fromJar;
    private int hopCooldown;
    private int rollTicks;
    private int alertTicks;
    private int startledTicks;
    private int chirpTicks;
    private int produceTimer;
    private int actionCooldown;
    private int clingTicks;
    private double climbTargetY;

    // general-purpose state for the expansion bugs' tricks (see SpecialBehaviors)
    public int specialCooldown;
    public int specialTimer;
    @Nullable
    public java.util.UUID owner;
    public boolean sitting;
    @Nullable
    public BlockPos home;
    @Nullable
    public net.minecraft.core.Holder<SoundEvent> pendingNote;
    public float notePitch = 1f;

    public BugEntity(EntityType<? extends BugEntity> type, Level level) {
        super(type, level);
        BugSpecies s = species();
        switch (s.movement()) {
            case FLY -> {
                this.moveControl = new FlyingMoveControl(this, 20, true);
                this.setPathfindingMalus(PathType.WATER, -1.0f);
                this.setPathfindingMalus(PathType.WATER_BORDER, 8.0f);
                this.setPathfindingMalus(PathType.FENCE, -1.0f);
            }
            case SKATE -> {
                this.setPathfindingMalus(PathType.WATER, 0.0f);
                this.setPathfindingMalus(PathType.WATER_BORDER, 0.0f);
            }
            case SWIM -> {
                this.moveControl = new net.minecraft.world.entity.ai.control.SmoothSwimmingMoveControl(this, 85, 10, 0.1f, 0.5f, true);
                this.lookControl = new net.minecraft.world.entity.ai.control.SmoothSwimmingLookControl(this, 10);
                this.setPathfindingMalus(PathType.WATER, 0.0f);
            }
            case AQUATIC -> {
                this.setPathfindingMalus(PathType.WATER, 0.0f);
                this.setPathfindingMalus(PathType.WATER_BORDER, 0.0f);
            }
            default -> {
            }
        }
        if (s.fireImmune()) {
            this.setPathfindingMalus(PathType.LAVA, 8.0f);
            this.setPathfindingMalus(PathType.DANGER_FIRE, 0.0f);
            this.setPathfindingMalus(PathType.DAMAGE_FIRE, 0.0f);
        }
        this.produceTimer = 2400 + random.nextInt(4800);
    }

    public static AttributeSupplier.Builder createAttributes(BugSpecies s) {
        return Mob.createMobAttributes()
                .add(Attributes.MAX_HEALTH, s.health())
                .add(Attributes.MOVEMENT_SPEED, s.speed())
                .add(Attributes.FLYING_SPEED, s.flySpeed())
                .add(Attributes.FOLLOW_RANGE, 16.0)
                .add(Attributes.KNOCKBACK_RESISTANCE, s == BugSpecies.HERCULES_BEETLE ? 0.6 : 0.0)
                .add(Attributes.ATTACK_DAMAGE, s == BugSpecies.CENTIPEDE ? 3.0 : s == BugSpecies.PAPER_WASP ? 2.0 : 1.0);
    }

    public BugSpecies species() {
        if (speciesCache == null) {
            speciesCache = BugSpecies.byType(getType());
        }
        return speciesCache;
    }

    // ------------------------------------------------------------------ synced state

    @Override
    protected void defineSynchedData(SynchedEntityData.Builder builder) {
        super.defineSynchedData(builder);
        builder.define(DATA_FLAGS, (byte) 0);
        builder.define(DATA_PRISMATIC, false);
        builder.define(DATA_SIZE, 1.0f);
        builder.define(DATA_CLING, (byte) -1);
    }

    public boolean hasFlag(int flag) {
        return (entityData.get(DATA_FLAGS) & flag) != 0;
    }

    public void setFlag(int flag, boolean on) {
        byte b = entityData.get(DATA_FLAGS);
        byte next = (byte) (on ? b | flag : b & ~flag);
        if (next != b) {
            entityData.set(DATA_FLAGS, next);
        }
    }

    public boolean isPrismatic() {
        return entityData.get(DATA_PRISMATIC);
    }

    public void setPrismatic(boolean prismatic) {
        entityData.set(DATA_PRISMATIC, prismatic);
    }

    /** Individual size variation, 0.85 - 1.15. */
    public float getSizeScale() {
        return entityData.get(DATA_SIZE);
    }

    /** Direction from this bug to the bark it clings to, or null. */
    @Nullable
    public Direction getClingFace() {
        byte b = entityData.get(DATA_CLING);
        return b < 0 ? null : Direction.from3DDataValue(b);
    }

    public boolean isClinging() {
        return getClingFace() != null;
    }

    public boolean isFromJar() {
        return fromJar;
    }

    public void setFromJar(boolean fromJar) {
        this.fromJar = fromJar;
    }

    // ------------------------------------------------------------------ navigation & movement

    @Override
    protected PathNavigation createNavigation(Level level) {
        BugSpecies s = species();
        return switch (s.movement()) {
            case FLY -> {
                FlyingPathNavigation nav = new FlyingPathNavigation(this, level);
                nav.setCanOpenDoors(false);
                nav.setCanFloat(false);
                nav.setCanPassDoors(true);
                yield nav;
            }
            case CLIMB -> new WallClimberNavigation(this, level);
            case SWIM -> new net.minecraft.world.entity.ai.navigation.WaterBoundPathNavigation(this, level);
            case AQUATIC -> new net.minecraft.world.entity.ai.navigation.AmphibiousPathNavigation(this, level);
            case SKATE -> new SkaterNavigation(this, level);
            default -> new GroundPathNavigation(this, level);
        };
    }

    /** Ground navigation that treats still water as solid ground, like the strider on lava. */
    static class SkaterNavigation extends GroundPathNavigation {
        SkaterNavigation(Mob mob, Level level) {
            super(mob, level);
        }

        @Override
        protected PathFinder createPathFinder(int maxVisitedNodes) {
            this.nodeEvaluator = new WalkNodeEvaluator();
            this.nodeEvaluator.setCanPassDoors(true);
            return new PathFinder(this.nodeEvaluator, maxVisitedNodes);
        }

        @Override
        protected boolean hasValidPathType(PathType pathType) {
            return pathType == PathType.WATER || pathType == PathType.WATER_BORDER || super.hasValidPathType(pathType);
        }

        @Override
        public boolean isStableDestination(BlockPos pos) {
            return level.getFluidState(pos).is(FluidTags.WATER) || super.isStableDestination(pos);
        }
    }

    @Override
    public boolean canStandOnFluid(FluidState fluid) {
        return species().movement() == Movement.SKATE && fluid.is(FluidTags.WATER);
    }

    @Override
    public boolean onClimbable() {
        return species().movement() == Movement.CLIMB && hasFlag(FLAG_CLIMBING);
    }

    @Override
    public boolean causeFallDamage(float distance, float multiplier, DamageSource source) {
        return false;
    }

    @Override
    protected void checkFallDamage(double y, boolean onGround, BlockState state, BlockPos pos) {
    }

    @Override
    public boolean isImmobile() {
        return super.isImmobile() || hasFlag(FLAG_ROLLED) || hasFlag(FLAG_FROZEN) || sitting
                || species() == BugSpecies.MOLE_CRICKET && hasFlag(FLAG_HIDDEN)
                || species() == BugSpecies.DARKLING_BEETLE && hasFlag(FLAG_ALERT);
    }

    @Override
    public void travel(Vec3 input) {
        if (species().movement() == Movement.SWIM && isInWater() && isEffectiveAi()) {
            moveRelative(getSpeed(), input);
            move(net.minecraft.world.entity.MoverType.SELF, getDeltaMovement());
            setDeltaMovement(getDeltaMovement().scale(0.9));
            return;
        }
        // hoppers only move by hopping: stand still between hops
        if (species().hasHop() && onGround() && hopCooldown > 0 && !level().isClientSide) {
            input = Vec3.ZERO;
        }
        super.travel(input);
    }

    @Override
    public boolean canBeLeashed() {
        return false;
    }

    /** Hitchhiking ticks ride along; they never steer. */
    @Override
    public boolean canControlVehicle() {
        return false;
    }

    private boolean waterBug() {
        Movement m = species().movement();
        return m == Movement.SKATE || m == Movement.SWIM || m == Movement.AQUATIC;
    }

    @Override
    public boolean isPushedByFluid() {
        return !waterBug() && super.isPushedByFluid();
    }

    @Override
    public boolean canDrownInFluidType(net.neoforged.neoforge.fluids.FluidType type) {
        return !waterBug() && super.canDrownInFluidType(type);
    }

    // ------------------------------------------------------------------ goals

    @Override
    protected void registerGoals() {
        BugSpecies s = species();
        Movement m = s.movement();
        if (m == Movement.HANG) {
            this.goalSelector.addGoal(8, new LookAtPlayerGoal(this, Player.class, 6.0f));
            return;
        }
        if (m != Movement.SKATE && m != Movement.FLY && m != Movement.SWIM && m != Movement.AQUATIC) {
            this.goalSelector.addGoal(0, new FloatGoal(this));
        }
        this.goalSelector.addGoal(1, new BugPanicGoal(this, 1.6));
        this.goalSelector.addGoal(2, new BreedGoal(this, 1.0));
        this.goalSelector.addGoal(3, new TemptGoal(this, 1.1, stack -> species().food().test(stack), false));

        switch (s) {
            case LADYBUG -> this.goalSelector.addGoal(4, new HuntAphidGoal(this));
            case APHID -> this.goalSelector.addGoal(4, new AvoidEntityGoal<>(this, BugEntity.class, 4.0f, 1.0, 1.3,
                    e -> e instanceof BugEntity b && b.species() == BugSpecies.LADYBUG));
            case CAVE_WETA -> this.goalSelector.addGoal(4, new AvoidEntityGoal<>(this, Player.class, 6.0f, 1.1, 1.5,
                    e -> !e.isShiftKeyDown() && !e.isSpectator()));
            case GOLDEN_SCARAB -> this.goalSelector.addGoal(4, new AvoidEntityGoal<>(this, Player.class, 8.0f, 1.2, 1.7,
                    e -> !e.isShiftKeyDown() && !e.isSpectator()));
            case MONARCH -> this.goalSelector.addGoal(5, new FlowerVisitGoal(this));
            case SILK_MOTH, VOID_MOTH -> this.goalSelector.addGoal(5, new LightOrbitGoal(this));
            case DUNG_BEETLE -> this.goalSelector.addGoal(6, new FollowLivestockGoal(this));
            case STAG_BEETLE -> this.goalSelector.addGoal(5, new SparGoal(this));
            default -> {
            }
        }
        Predicate<BlockState> bark = barkFor(s);
        if (bark != null) {
            this.goalSelector.addGoal(6, new ClingGoal(this, bark));
        }
        SpecialBehaviors.addGoals(this, this.goalSelector, this.targetSelector);

        if (m == Movement.FLY) {
            this.goalSelector.addGoal(5, new RestGoal(this));
            this.goalSelector.addGoal(7, new BugFlyGoal(this));
        } else if (m == Movement.SKATE || m == Movement.AQUATIC) {
            this.goalSelector.addGoal(7, new RandomStrollGoal(this, 0.9));
        } else if (m == Movement.SWIM) {
            this.goalSelector.addGoal(7, new net.minecraft.world.entity.ai.goal.RandomSwimmingGoal(this, 1.0, 20));
        } else if (s == BugSpecies.PRAYING_MANTIS || s == BugSpecies.ANTLION) {
            // ambush hunters barely move
            this.goalSelector.addGoal(7, new WaterAvoidingRandomStrollGoal(this, 0.6, 0.01f));
        } else {
            this.goalSelector.addGoal(7, new WaterAvoidingRandomStrollGoal(this, 0.8));
        }
        this.goalSelector.addGoal(8, new LookAtPlayerGoal(this, Player.class, 6.0f));
        this.goalSelector.addGoal(9, new RandomLookAroundGoal(this));
    }

    /** The bark a tree-dwelling bug likes to cling to, or null if it does not climb trees. */
    @Nullable
    public static Predicate<BlockState> barkFor(BugSpecies species) {
        return switch (species) {
            case JEWEL_BEETLE -> st -> st.is(Blocks.BIRCH_LOG);
            case STAG_BEETLE -> st -> st.is(Blocks.OAK_LOG) || st.is(Blocks.DARK_OAK_LOG);
            case HERCULES_BEETLE -> st -> st.is(Blocks.JUNGLE_LOG);
            case CICADA -> st -> st.is(Blocks.ACACIA_LOG);
            case ORB_WEAVER -> st -> st.is(BlockTags.LOGS);
            case LADYBUG -> st -> st.is(BlockTags.LOGS);
            default -> null;
        };
    }

    // ------------------------------------------------------------------ ticking

    @Override
    public void tick() {
        super.tick();
        if (level().isClientSide) {
            clientTick();
            return;
        }
        BugSpecies s = species();
        if (startledTicks > 0) startledTicks--;
        if (actionCooldown > 0) actionCooldown--;
        if (specialCooldown > 0) specialCooldown--;
        switch (s.movement()) {
            case CLIMB -> setFlag(FLAG_CLIMBING, horizontalCollision && !isClinging());
            case HANG -> tickHanging();
            case SKATE -> floatOnWater();
            case HOP -> tickHopping();
            default -> {
            }
        }
        if (isClinging()) {
            tickClinging();
        }
        switch (s) {
            case PILL_BUG, MILLIPEDE, GIANT_ISOPOD -> tickPillBug();
            case WALKING_STICK -> {
                if (tickCount % 5 == 0) setFlag(FLAG_FROZEN, isWatched());
            }
            case SCULK_MITE -> tickSculkMite();
            case CRICKET -> tickCricket();
            case LADYBUG -> tickLadybug();
            case DUNG_BEETLE -> tickDungBeetle();
            case HERCULES_BEETLE -> {
                if (actionCooldown == 0 && tickCount % 20 == 0 && level().getNearestPlayer(this, 4.0) != null) {
                    triggerAnim("action", "horn");
                    actionCooldown = 100;
                }
            }
            default -> {
            }
        }
        SpecialBehaviors.serverTick(this);
    }

    private void clientTick() {
        SpecialBehaviors.clientTick(this);
        BugSpecies s = species();
        ParticleOptions particle = null;
        int chance = 0;
        if (isPrismatic()) {
            float hue = (tickCount % 60) / 60f;
            int rgb = Mth.hsvToRgb(hue, 0.7f, 1.0f);
            particle = ColorParticleOption.create(ParticleTypes.ENTITY_EFFECT, 0xFF000000 | rgb);
            chance = 8;
        } else if (s == BugSpecies.VOID_MOTH) {
            particle = ParticleTypes.PORTAL;
            chance = 6;
        } else if (s == BugSpecies.EMBER_BEETLE) {
            particle = ParticleTypes.SMALL_FLAME;
            chance = 30;
        } else if (s == BugSpecies.SCULK_MITE) {
            particle = ParticleTypes.SCULK_CHARGE_POP;
            chance = 40;
        } else if (s.rarity() == BugRarity.LEGENDARY) {
            particle = ParticleTypes.END_ROD;
            chance = 25;
        } else if (s.rarity() == BugRarity.EPIC) {
            particle = ParticleTypes.ELECTRIC_SPARK;
            chance = 35;
        } else if (s.rarity() == BugRarity.RARE && s != BugSpecies.WALKING_STICK && s != BugSpecies.LEAF_INSECT) {
            particle = ParticleTypes.GLOW;
            chance = 60;
        }
        if (particle != null && random.nextInt(chance) == 0) {
            level().addParticle(particle, getRandomX(0.6), getY() + getBbHeight() * random.nextDouble(), getRandomZ(0.6),
                    (random.nextDouble() - 0.5) * 0.02, 0.02, (random.nextDouble() - 0.5) * 0.02);
        }
    }

    private void floatOnWater() {
        if (isInWater()) {
            CollisionContext ctx = CollisionContext.of(this);
            if (ctx.isAbove(LiquidBlock.STABLE_SHAPE, blockPosition(), true)
                    && !level().getFluidState(blockPosition().above()).is(FluidTags.WATER)) {
                setOnGround(true);
            } else {
                setDeltaMovement(getDeltaMovement().scale(0.5).add(0.0, 0.05, 0.0));
            }
        }
    }

    private void tickHopping() {
        if (hopCooldown > 0) {
            hopCooldown--;
            return;
        }
        if (onGround() && !getNavigation().isDone()) {
            var path = getNavigation().getPath();
            if (path != null && !path.isDone()) {
                Vec3 next = path.getNextEntityPos(this);
                Vec3 dir = new Vec3(next.x - getX(), 0, next.z - getZ());
                if (dir.lengthSqr() > 1.0E-4) {
                    dir = dir.normalize();
                    double power = getSpeed() > 0.25 ? 0.42 : 0.3;
                    setDeltaMovement(dir.x * power, 0.36 + random.nextDouble() * 0.08, dir.z * power);
                    setYRot((float) (Mth.atan2(dir.z, dir.x) * Mth.RAD_TO_DEG) - 90.0f);
                    yBodyRot = getYRot();
                    hasImpulse = true;
                    playSound(SoundEvents.SILVERFISH_STEP, 0.15f, 1.8f);
                }
            }
            hopCooldown = 6 + random.nextInt(10);
        }
    }

    private void tickHanging() {
        BlockPos above = BlockPos.containing(getX(), getBoundingBox().maxY + 0.05, getZ());
        boolean attached = level().getBlockState(above).isFaceSturdy(level(), above, Direction.DOWN);
        if (attached) {
            setNoGravity(true);
            setDeltaMovement(Vec3.ZERO);
        } else {
            setNoGravity(false);
            if (onGround() && tickCount % 40 == 0) {
                attachToCeiling();
            }
        }
    }

    /** Moves a hanging bug up to the nearest ceiling within 6 blocks, if any. */
    public void attachToCeiling() {
        BlockPos.MutableBlockPos pos = blockPosition().mutable();
        for (int i = 0; i < 6; i++) {
            BlockPos up = pos.above();
            BlockState state = level().getBlockState(up);
            if (!state.isAir()) {
                if (state.isFaceSturdy(level(), up, Direction.DOWN)) {
                    moveTo(getX(), up.getY() - getBbHeight() - 0.01, getZ(), getYRot(), 0);
                    setNoGravity(true);
                }
                return;
            }
            pos.move(Direction.UP);
        }
    }

    // ------------------------------------------------------------------ clinging to bark

    /** Starts climbing up the trunk in direction face, to about climbBlocks above here. */
    public void startCling(Direction face, double climbBlocks, int holdTicks) {
        entityData.set(DATA_CLING, (byte) face.get3DDataValue());
        BlockPos here = blockPosition();
        double off = 0.5 - getBbWidth() / 2 - 0.02;
        setPos(here.getX() + 0.5 + face.getStepX() * off, getY(), here.getZ() + 0.5 + face.getStepZ() * off);
        climbTargetY = getY() + climbBlocks;
        clingTicks = holdTicks;
        setNoGravity(true);
        setDeltaMovement(Vec3.ZERO);
        getNavigation().stop();
    }

    public void stopCling() {
        entityData.set(DATA_CLING, (byte) -1);
        setNoGravity(false);
    }

    private void tickClinging() {
        Direction face = getClingFace();
        BlockPos bark = BlockPos.containing(getX(), getY() + 0.1, getZ()).relative(face);
        if (!level().getBlockState(bark).isSolid() || clingTicks-- <= 0) {
            stopCling();
            return;
        }
        setDeltaMovement(Vec3.ZERO);
        setYRot(face.toYRot());
        yBodyRot = getYRot();
        yHeadRot = getYRot();
        if (getY() < climbTargetY) {
            BlockPos head = BlockPos.containing(getX(), getY() + getBbHeight() + 0.1, getZ());
            if (level().getBlockState(head).isAir() && level().getBlockState(head.relative(face)).isSolid()) {
                setPos(getX(), getY() + 0.04, getZ());
                setFlag(FLAG_CLIMBING, true);
            } else {
                climbTargetY = getY();
            }
        } else {
            setFlag(FLAG_CLIMBING, false);
        }
    }

    // ------------------------------------------------------------------ species tricks

    private void tickPillBug() {
        if (rollTicks > 0) {
            rollTicks--;
            getNavigation().stop();
            if (rollTicks == 0) {
                Player near = level().getNearestPlayer(this, 2.5);
                if (near != null && !near.isShiftKeyDown()) {
                    rollTicks = 40;
                } else {
                    setFlag(FLAG_ROLLED, false);
                }
            }
        } else if (tickCount % 5 == 0) {
            Player near = level().getNearestPlayer(this, 2.5);
            if (near != null && !near.isShiftKeyDown() && !near.isSpectator()) {
                rollUp();
            }
        }
    }

    public void rollUp() {
        rollTicks = 80 + random.nextInt(60);
        setFlag(FLAG_ROLLED, true);
        getNavigation().stop();
    }

    private boolean isWatched() {
        for (Player player : level().getEntitiesOfClass(Player.class, getBoundingBox().inflate(16))) {
            if (player.isSpectator()) continue;
            Vec3 view = player.getViewVector(1.0f).normalize();
            Vec3 to = new Vec3(getX() - player.getX(), getY(0.5) - player.getEyeY(), getZ() - player.getZ());
            double dist = to.length();
            if (view.dot(to.normalize()) > 1.0 - 0.08 / Math.max(1.0, dist * 0.3) && player.hasLineOfSight(this)) {
                return true;
            }
        }
        return false;
    }

    private void tickSculkMite() {
        if (tickCount % 5 != 0) return;
        Player loud = null;
        for (Player player : level().getEntitiesOfClass(Player.class, getBoundingBox().inflate(8))) {
            if (player.isSpectator() || player.isShiftKeyDown()) continue;
            if (player.isSprinting() || player.getKnownMovement().horizontalDistanceSqr() > 0.0004) {
                loud = player;
                break;
            }
        }
        if (loud != null) {
            alertTicks += 5;
            setFlag(FLAG_ALERT, true);
            getNavigation().stop();
            getLookControl().setLookAt(loud);
            if (alertTicks == 5) {
                playSound(SoundEvents.SCULK_CLICKING, 0.6f, 1.6f);
            }
            if (alertTicks >= 40) {
                burrowAway(loud);
            }
        } else if (alertTicks > 0) {
            alertTicks = Math.max(0, alertTicks - 5);
            if (alertTicks == 0) setFlag(FLAG_ALERT, false);
        }
    }

    private void burrowAway(Player cause) {
        if (level() instanceof ServerLevel server) {
            server.sendParticles(ParticleTypes.SCULK_SOUL, getX(), getY() + 0.2, getZ(), 8, 0.2, 0.1, 0.2, 0.02);
            server.playSound(null, blockPosition(), SoundEvents.SCULK_BLOCK_SPREAD, SoundSource.NEUTRAL, 1.0f, 1.2f);
            if (cause instanceof ServerPlayer sp) {
                sp.displayClientMessage(net.minecraft.network.chat.Component.translatable("bugslife.msg.mite_burrowed"), true);
                ModTriggers.BUG_ACTION.get().trigger(sp, "spook_mite");
            }
        }
        discard();
    }

    private void tickCricket() {
        if (chirpTicks > 0) {
            chirpTicks--;
            if (chirpTicks % 3 == 0) {
                playSound(SoundEvents.NOTE_BLOCK_HAT.value(), 0.35f, 1.9f + random.nextFloat() * 0.1f);
            }
        } else if (!level().isDay() && random.nextInt(160) == 0) {
            chirpTicks = 18;
            triggerAnim("action", "chirp");
        }
    }

    private void tickLadybug() {
        // ladybugs are a gardener's friend: crops they sit on grow a little faster
        if (tickCount % 80 == 0 && random.nextInt(3) == 0 && level() instanceof ServerLevel server) {
            BlockPos pos = blockPosition();
            BlockState state = server.getBlockState(pos);
            if (state.is(BlockTags.CROPS) && state.isRandomlyTicking()) {
                state.randomTick(server, pos, random);
                server.sendParticles(ParticleTypes.HAPPY_VILLAGER, pos.getX() + 0.5, pos.getY() + 0.5, pos.getZ() + 0.5, 2, 0.2, 0.2, 0.2, 0);
            }
        }
    }

    private void tickDungBeetle() {
        if (--produceTimer <= 0) {
            produceTimer = 4800 + random.nextInt(4800);
            if (!fromJar || random.nextBoolean()) {
                spawnAtLocation(new ItemStack(ModItems.FRASS.get()));
            }
        }
    }

    /** Short-range teleport, used by the void moth when spooked. */
    public boolean blink() {
        for (int i = 0; i < 16; i++) {
            double x = getX() + (random.nextDouble() - 0.5) * 12;
            double y = getY() + random.nextInt(5) - 2;
            double z = getZ() + (random.nextDouble() - 0.5) * 12;
            if (randomTeleport(x, y, z, true)) {
                level().playSound(null, xo, yo, zo, SoundEvents.ENDERMAN_TELEPORT, getSoundSource(), 0.4f, 1.8f);
                playSound(SoundEvents.ENDERMAN_TELEPORT, 0.4f, 1.8f);
                return true;
            }
        }
        return false;
    }

    /** Called when a net swing misses: the bug bolts (and some fight back). */
    public void startle(Player player) {
        SpecialBehaviors.onStartle(this, player);
        startle();
    }

    public void startle() {
        startledTicks = 60;
        if (isClinging()) stopCling();
        if (species() == BugSpecies.VOID_MOTH) {
            blink();
        } else if (SpecialBehaviors.ROLLERS.contains(species())) {
            rollUp();
        }
    }

    public boolean isStartled() {
        return startledTicks > 0;
    }

    @Override
    public boolean hurt(DamageSource source, float amount) {
        if (hasFlag(FLAG_ROLLED)) {
            amount *= 0.25f;
        }
        boolean hurt = super.hurt(source, amount);
        if (hurt && !level().isClientSide && isAlive()) {
            if (isClinging()) stopCling();
            if (species() == BugSpecies.VOID_MOTH) blink();
            if (SpecialBehaviors.ROLLERS.contains(species())) rollUp();
            SpecialBehaviors.onHurt(this, source);
        }
        return hurt;
    }

    // ------------------------------------------------------------------ breeding & spawning

    @Override
    public boolean isFood(ItemStack stack) {
        return species().canEat() && species().food().test(stack);
    }

    @Override
    public net.minecraft.world.InteractionResult mobInteract(Player player, net.minecraft.world.InteractionHand hand) {
        net.minecraft.world.InteractionResult special = SpecialBehaviors.interact(this, player, hand);
        return special != null ? special : super.mobInteract(player, hand);
    }

    @Override
    public boolean doHurtTarget(net.minecraft.world.entity.Entity target) {
        boolean hit = super.doHurtTarget(target);
        if (hit && species() == BugSpecies.PAPER_WASP && target instanceof LivingEntity living) {
            living.addEffect(new net.minecraft.world.effect.MobEffectInstance(net.minecraft.world.effect.MobEffects.POISON, 60, 0), this);
        }
        return hit;
    }

    @Nullable
    @Override
    public AgeableMob getBreedOffspring(ServerLevel level, AgeableMob partner) {
        BugEntity child = ModEntities.get(species()).get().create(level);
        if (child != null) {
            boolean parentPrismatic = isPrismatic() || (partner instanceof BugEntity b && b.isPrismatic());
            child.setPrismatic(random.nextInt(parentPrismatic ? 4 : 64) == 0);
            child.fromJar = true;
        }
        return child;
    }

    @Override
    public void setAge(int age) {
        // bugs grow up four times faster than other animals
        super.setAge(age < 0 ? Math.max(age, -6000) : age);
    }

    @Nullable
    @Override
    public SpawnGroupData finalizeSpawn(ServerLevelAccessor level, DifficultyInstance difficulty, MobSpawnType spawnType,
                                        @Nullable SpawnGroupData groupData) {
        entityData.set(DATA_SIZE, 0.85f + random.nextFloat() * 0.3f);
        if (spawnType != MobSpawnType.BREEDING && random.nextInt(WILD_PRISMATIC_CHANCE) == 0) {
            setPrismatic(true);
        }
        if (species().movement() == Movement.HANG) {
            attachToCeiling();
        }
        return super.finalizeSpawn(level, difficulty, spawnType, groupData);
    }

    @Override
    public boolean removeWhenFarAway(double distanceToClosestPlayer) {
        return !fromJar && owner == null;
    }

    @Override
    public boolean checkSpawnRules(net.minecraft.world.level.LevelAccessor level, MobSpawnType reason) {
        return true;
    }

    public BugData toData() {
        return new BugData(species(), isPrismatic(), isBaby());
    }

    public static BugEntity fromData(Level level, BugData data) {
        BugEntity bug = ModEntities.get(data.species()).get().create(level);
        if (bug != null) {
            bug.setPrismatic(data.prismatic());
            if (data.baby()) bug.setAge(-6000);
            bug.fromJar = true;
        }
        return bug;
    }

    // ------------------------------------------------------------------ saving

    @Override
    public void addAdditionalSaveData(CompoundTag tag) {
        super.addAdditionalSaveData(tag);
        tag.putBoolean("Prismatic", isPrismatic());
        tag.putBoolean("FromJar", fromJar);
        tag.putFloat("Size", getSizeScale());
        tag.putInt("ProduceTimer", produceTimer);
        if (owner != null) tag.putUUID("Owner", owner);
        tag.putBoolean("Sitting", sitting);
    }

    @Override
    public void readAdditionalSaveData(CompoundTag tag) {
        super.readAdditionalSaveData(tag);
        setPrismatic(tag.getBoolean("Prismatic"));
        fromJar = tag.getBoolean("FromJar");
        if (tag.contains("Size")) entityData.set(DATA_SIZE, tag.getFloat("Size"));
        if (tag.contains("ProduceTimer")) produceTimer = tag.getInt("ProduceTimer");
        owner = tag.hasUUID("Owner") ? tag.getUUID("Owner") : null;
        sitting = tag.getBoolean("Sitting");
    }

    // ------------------------------------------------------------------ sounds

    @Nullable
    @Override
    protected SoundEvent getAmbientSound() {
        return null;
    }

    @Override
    protected SoundEvent getHurtSound(DamageSource source) {
        return SoundEvents.SILVERFISH_HURT;
    }

    @Override
    protected SoundEvent getDeathSound() {
        return SoundEvents.SILVERFISH_DEATH;
    }

    @Override
    protected void playStepSound(BlockPos pos, BlockState state) {
        if (!species().flies()) {
            playSound(SoundEvents.SILVERFISH_STEP, 0.05f, 1.6f);
        }
    }

    @Override
    public float getVoicePitch() {
        return 1.7f + random.nextFloat() * 0.3f;
    }

    @Override
    protected float getSoundVolume() {
        return 0.4f;
    }

    @Override
    protected int getBaseExperienceReward() {
        return random.nextInt(2);
    }

    // ------------------------------------------------------------------ GeckoLib

    private record Anims(RawAnimation idle, RawAnimation walk, RawAnimation fly, RawAnimation hop, RawAnimation extra) {
    }

    private static final Map<BugSpecies, Anims> ANIMS = new EnumMap<>(BugSpecies.class);

    private static Anims anims(BugSpecies s) {
        return ANIMS.computeIfAbsent(s, sp -> {
            String p = "animation." + sp.id() + ".";
            RawAnimation extra = null;
            if (sp.extraAnim() != null) {
                extra = "roll".equals(sp.extraAnim()) || "curl".equals(sp.extraAnim())
                        ? RawAnimation.begin().thenPlayAndHold(p + sp.extraAnim())
                        : RawAnimation.begin().thenLoop(p + sp.extraAnim());
            }
            return new Anims(
                    RawAnimation.begin().thenLoop(p + "idle"),
                    sp.hasWalk() ? RawAnimation.begin().thenLoop(p + "walk") : null,
                    sp.hasFly() ? RawAnimation.begin().thenLoop(p + "fly") : null,
                    sp.hasHop() ? RawAnimation.begin().thenPlay(p + "hop") : null,
                    extra);
        });
    }

    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "main", 3, this::mainAnimation));
        String action = species().actionAnim();
        if (action != null) {
            controllers.add(new AnimationController<>(this, "action", 2, state -> PlayState.STOP)
                    .triggerableAnim(action, RawAnimation.begin().thenPlay("animation." + species().id() + "." + action)));
        }
    }

    private PlayState mainAnimation(AnimationState<BugEntity> state) {
        BugSpecies s = species();
        Anims a = anims(s);
        if (a.extra() != null && (hasFlag(FLAG_ROLLED) || hasFlag(FLAG_ALERT))) {
            return state.setAndContinue(a.extra());
        }
        if (s.movement() == Movement.HANG) {
            return state.setAndContinue(a.idle());
        }
        boolean moving = state.isMoving() || hasFlag(FLAG_CLIMBING);
        boolean airborne = !onGround() && !isInWater() && !isClinging() && !hasFlag(FLAG_CLIMBING);
        if (s.flies()) {
            if (airborne && a.fly() != null) return state.setAndContinue(a.fly());
            if (moving && a.walk() != null) return state.setAndContinue(a.walk());
            return state.setAndContinue(a.idle());
        }
        if (airborne && a.hop() != null) {
            return state.setAndContinue(a.hop());
        }
        if (airborne && a.fly() != null && getDeltaMovement().y < -0.1) {
            return state.setAndContinue(a.fly());
        }
        if (moving && a.walk() != null && !hasFlag(FLAG_FROZEN)) {
            return state.setAndContinue(a.walk());
        }
        return state.setAndContinue(a.idle());
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return geoCache;
    }

    /** Firefly flash brightness 0-1. Fireflies near each other flash in step (as real synchronous fireflies do). */
    public float glowStrength(float partialTick) {
        float special = SpecialBehaviors.glowStrength(this, partialTick);
        if (special >= 0) return special;
        BugSpecies s = species();
        if (s == BugSpecies.FIREFLY) {
            if (level().isDay() && onGround()) return 0.15f;
            float t = (level().getGameTime() % 50) + partialTick + (getId() % 3);
            float pulse = t < 12 ? Mth.sin(t / 12f * Mth.PI) : 0f;
            return 0.1f + 0.9f * pulse;
        }
        if (s == BugSpecies.SCULK_MITE && hasFlag(FLAG_ALERT)) {
            return 0.6f + 0.4f * Mth.sin((tickCount + partialTick) * 0.8f);
        }
        return 1.0f;
    }
}
