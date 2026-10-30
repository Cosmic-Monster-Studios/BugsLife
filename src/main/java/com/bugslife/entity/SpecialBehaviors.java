package com.bugslife.entity;

import com.bugslife.bug.BugSpecies;
import com.bugslife.entity.goal.CircleSwimGoal;
import com.bugslife.entity.goal.EatDroppedItemsGoal;
import com.bugslife.entity.goal.FlockGoal;
import com.bugslife.entity.goal.FlowerVisitGoal;
import com.bugslife.entity.goal.FollowLeaderGoal;
import com.bugslife.entity.goal.FollowOwnerGoal;
import com.bugslife.entity.goal.LightOrbitGoal;
import com.bugslife.entity.goal.MosquitoBiteGoal;
import com.bugslife.entity.goal.PredatorGoal;
import com.bugslife.entity.goal.RideAnimalGoal;
import com.bugslife.entity.goal.SeekDarkGoal;
import com.bugslife.entity.goal.SpinWebGoal;
import com.bugslife.registry.ModItems;
import com.bugslife.registry.ModTriggers;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.core.Holder;
import net.minecraft.core.particles.BlockParticleOption;
import net.minecraft.core.particles.ColorParticleOption;
import net.minecraft.core.particles.ParticleOptions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.ItemTags;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.AreaEffectCloud;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LightningBolt;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.AvoidEntityGoal;
import net.minecraft.world.entity.ai.goal.GoalSelector;
import net.minecraft.world.entity.ai.goal.MeleeAttackGoal;
import net.minecraft.world.entity.ai.goal.target.NearestAttackableTargetGoal;
import net.minecraft.world.entity.monster.Endermite;
import net.minecraft.world.entity.monster.Phantom;
import net.minecraft.world.entity.monster.Silverfish;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.ItemUtils;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.NoteBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.event.VanillaGameEvent;
import net.neoforged.neoforge.event.entity.living.LivingChangeTargetEvent;
import net.neoforged.neoforge.event.level.NoteBlockEvent;
import org.jetbrains.annotations.Nullable;

import java.util.Collections;
import java.util.EnumSet;
import java.util.Set;
import java.util.WeakHashMap;

import static com.bugslife.bug.BugSpecies.*;

/**
 * The expansion bugs' special tricks: extra goals, per-tick behaviour, defences, interactions, glow, particles and
 * the world events some of them react to (note blocks, vibrations, phantoms).
 */
public final class SpecialBehaviors {
    private SpecialBehaviors() {
    }

    /** Small bugs that predators eat. */
    public static final Set<BugSpecies> SMALL_PREY = EnumSet.of(APHID, MOSQUITO, MAYFLY, SPRINGTAIL, TERMITE, TICK, WORKER_ANT,
            FIREFLY, CRICKET, GRASSHOPPER, LADYBUG, BOOKWORM);

    /** Bugs that roll or curl up when threatened. */
    public static final Set<BugSpecies> ROLLERS = EnumSet.of(PILL_BUG, MILLIPEDE, GIANT_ISOPOD);

    // echo moths and owl butterflies are looked up by every vibration and every phantom target change
    private static final Set<BugEntity> ECHO_MOTHS = Collections.newSetFromMap(new WeakHashMap<>());
    private static final Set<BugEntity> OWL_BUTTERFLIES = Collections.newSetFromMap(new WeakHashMap<>());

    private static boolean isSmallPrey(BugEntity b) {
        return SMALL_PREY.contains(b.species());
    }

    /** Whether the bug may change blocks in the world (respects the mobGriefing game rule and NeoForge's event). */
    public static boolean canGrief(BugEntity bug) {
        return net.neoforged.neoforge.event.EventHooks.canEntityGrief(bug.level(), bug);
    }

    // ================================================================== goals

    public static void addGoals(BugEntity bug, GoalSelector goals, GoalSelector targets) {
        switch (bug.species()) {
            case WORKER_ANT -> goals.addGoal(5, new FollowLeaderGoal(bug));
            case EARWIG -> goals.addGoal(4, new SeekDarkGoal(bug));
            case TERMITE -> goals.addGoal(4, new EatDroppedItemsGoal(bug, s -> s.is(ItemTags.PLANKS) || s.is(ItemTags.LOGS)
                    || s.is(ItemTags.SAPLINGS) || s.is(Items.STICK) || s.is(Items.BOWL) || s.is(ItemTags.WOODEN_SLABS)));
            case MOSQUITO -> goals.addGoal(4, new MosquitoBiteGoal(bug));
            case ORB_WEAVER -> {
                goals.addGoal(4, new PredatorGoal(bug, PredatorGoal.Style.STALK, 6,
                        b -> b.species().flies() && b.level().getBlockState(b.blockPosition()).is(Blocks.COBWEB)));
                goals.addGoal(5, new SpinWebGoal(bug));
            }
            case TICK -> goals.addGoal(5, new RideAnimalGoal(bug));
            case CENTIPEDE -> {
                goals.addGoal(3, new MeleeAttackGoal(bug, 1.4, true));
                targets.addGoal(1, new NearestAttackableTargetGoal<>(bug, Silverfish.class, true));
                targets.addGoal(2, new NearestAttackableTargetGoal<>(bug, Endermite.class, true));
            }
            case JUMPING_SPIDER -> goals.addGoal(4, new PredatorGoal(bug, PredatorGoal.Style.POUNCE, 4, SpecialBehaviors::isSmallPrey));
            case PRAYING_MANTIS -> goals.addGoal(4, new PredatorGoal(bug, PredatorGoal.Style.AMBUSH, 1.8, SpecialBehaviors::isSmallPrey));
            case HAWK_MOTH -> goals.addGoal(5, new FlowerVisitGoal(bug, true));
            case SAKURA_MOTH -> goals.addGoal(5, new FlowerVisitGoal(bug));
            case LUNA_MOTH -> goals.addGoal(5, new LightOrbitGoal(bug));
            case SOUL_MOTH -> goals.addGoal(5, new LightOrbitGoal(bug, s -> s.is(Blocks.SOUL_FIRE) || s.is(Blocks.SOUL_TORCH)
                    || s.is(Blocks.SOUL_WALL_TORCH) || s.is(Blocks.SOUL_LANTERN) || s.is(Blocks.SOUL_CAMPFIRE)));
            case PAPER_WASP -> {
                goals.addGoal(2, new MeleeAttackGoal(bug, 1.5, true));
                goals.addGoal(5, new FlowerVisitGoal(bug));
            }
            case LOCUST -> goals.addGoal(6, new FlockGoal(bug));
            case WHIRLIGIG_BEETLE -> goals.addGoal(6, new CircleSwimGoal(bug));
            case GRASSHOPPER -> goals.addGoal(4, new AvoidEntityGoal<>(bug, Player.class, 5.0f, 1.2, 1.6, e -> !e.isShiftKeyDown() && !e.isSpectator()));
            case TARANTULA -> goals.addGoal(2, new FollowOwnerGoal(bug));
            default -> {
            }
        }
    }

    // ================================================================== server tick

    public static void serverTick(BugEntity bug) {
        ServerLevel level = (ServerLevel) bug.level();
        switch (bug.species()) {
            case MOSQUITO -> {
                if (bug.hasFlag(BugEntity.FLAG_ALERT) && --bug.specialTimer <= 0) bug.setFlag(BugEntity.FLAG_ALERT, false);
            }
            case MAYFLY -> {
                // an adult mayfly lives only a few minutes
                if (!bug.isFromJar() && bug.tickCount > 3600 + (bug.getId() % 1200)) vanish(bug, ParticleTypes.POOF);
            }
            case RAIN_BEETLE -> {
                if (!bug.isFromJar() && !level.isRaining() && ++bug.specialTimer > 100) burrow(bug);
            }
            case CICADA -> {
                if (level.isDay() && bug.isClinging()) {
                    if (bug.specialCooldown == 0 && bug.getRandom().nextInt(300) == 0) {
                        bug.triggerAnim("action", "buzz");
                        for (int i = 0; i < 3; i++) {
                            bug.playSound(SoundEvents.BEE_LOOP_AGGRESSIVE, 0.9f, 1.9f + i * 0.05f);
                        }
                        bug.specialCooldown = 200;
                    }
                    if (bug.getRandom().nextInt(9000) == 0) {
                        bug.spawnAtLocation(new ItemStack(ModItems.CICADA_SHELL.get()));
                    }
                }
            }
            case JUMPING_SPIDER -> {
                if (bug.specialCooldown == 0 && bug.tickCount % 20 == 0) {
                    Player p = level.getNearestPlayer(bug, 5);
                    if (p != null && isShiny(p.getMainHandItem())) {
                        bug.triggerAnim("action", "dance");
                        bug.getLookControl().setLookAt(p);
                        bug.specialCooldown = 60;
                    }
                }
            }
            case ANTLION -> tickAntlion(bug, level);
            case EARWIG -> {
                if (bug.specialCooldown == 0 && bug.tickCount % 10 == 0 && level.getNearestPlayer(bug, 1.5) != null) {
                    bug.triggerAnim("action", "pinch");
                    bug.specialCooldown = 40;
                }
            }
            case SPRINGTAIL, GRASSHOPPER -> {
                if (bug.specialCooldown == 0 && bug.onGround() && bug.tickCount % 5 == 0) {
                    Player p = level.getNearestPlayer(bug, bug.species() == SPRINGTAIL ? 2.5 : 3.5);
                    if (p != null && !p.isShiftKeyDown() && !p.isSpectator()) leapAway(bug, p.position());
                }
            }
            case ICE_CRAWLER -> {
                if (bug.tickCount % 40 == 0 && overheating(bug)) {
                    bug.hurt(bug.damageSources().hotFloor(), 1.0f);
                    level.sendParticles(ParticleTypes.FALLING_WATER, bug.getX(), bug.getY() + 0.2, bug.getZ(), 3, 0.1, 0.1, 0.1, 0);
                }
            }
            case MOLE_CRICKET -> tickMoleCricket(bug, level);
            case DARKLING_BEETLE -> {
                long t = level.getDayTime() % 24000L;
                boolean dawn = level.dimensionType().hasFixedTime() ? false : (t > 22500 || t < 1500);
                bug.setFlag(BugEntity.FLAG_ALERT, dawn);
                if (dawn) bug.getNavigation().stop();
            }
            case TARANTULA -> {
                if (bug.sitting) bug.getNavigation().stop();
            }
            case TICK -> {
                if (bug.isPassenger() && --bug.specialTimer <= 0) bug.stopRiding();
            }
            case PAPER_WASP -> {
                // the swarm calms down after half a minute
                if (bug.getTarget() != null && --bug.specialTimer <= 0) bug.setTarget(null);
            }
            case ECHO_MOTH -> ECHO_MOTHS.add(bug);
            case OWL_BUTTERFLY -> {
                OWL_BUTTERFLIES.add(bug);
                if (bug.tickCount % 20 == 0) {
                    for (Phantom phantom : level.getEntitiesOfClass(Phantom.class, bug.getBoundingBox().inflate(24))) {
                        if (phantom.getTarget() != null) {
                            phantom.setTarget(null);
                            phantom.setDeltaMovement(phantom.getDeltaMovement().add(0, 0.6, 0));
                        }
                    }
                }
            }
            case SAKURA_MOTH -> {
                if (bug.getRandom().nextInt(1500) == 0) scatterPetals(bug, level);
            }
            case MUSHROOM_BEETLE -> {
                if (bug.getRandom().nextInt(2000) == 0) plantMushroom(bug, level);
            }
            case CHORUS_WEEVIL -> {
                if (bug.specialCooldown == 0 && bug.getRandom().nextInt(300) == 0) chorusHop(bug, level);
            }
            case GUST_MOTH -> {
                if (bug.specialCooldown == 0 && bug.tickCount % 5 == 0) {
                    Player p = level.getNearestPlayer(bug, 2.5);
                    if (p != null && !p.isShiftKeyDown() && !p.isSpectator()) gust(bug, level, p);
                }
            }
            case SHULKER_MITE -> {
                if (bug.specialCooldown == 0 && bug.tickCount % 5 == 0) {
                    for (Player p : level.getEntitiesOfClass(Player.class, bug.getBoundingBox().inflate(0.6))) {
                        if (!p.isSpectator()) {
                            p.addEffect(new MobEffectInstance(MobEffects.LEVITATION, 40, 0), bug);
                            bug.playSound(SoundEvents.SHULKER_SHOOT, 0.5f, 1.6f);
                            bug.specialCooldown = 100;
                        }
                    }
                }
            }
            case STORM_BEETLE -> {
                if (bug.hasFlag(BugEntity.FLAG_ALERT) && --bug.specialTimer <= 0) bug.setFlag(BugEntity.FLAG_ALERT, false);
                if (level.isThundering() && bug.specialCooldown == 0 && bug.getRandom().nextInt(400) == 0 && level.canSeeSky(bug.blockPosition())) {
                    LightningBolt bolt = EntityType.LIGHTNING_BOLT.create(level);
                    if (bolt != null) {
                        bolt.moveTo(bug.getX(), bug.getY(), bug.getZ());
                        bolt.setVisualOnly(true);
                        level.addFreshEntity(bolt);
                    }
                    bug.setFlag(BugEntity.FLAG_ALERT, true);
                    bug.specialTimer = 400;
                    bug.specialCooldown = 600;
                }
            }
            case KATYDID -> {
                if (bug.pendingNote != null && --bug.specialTimer <= 0) {
                    bug.triggerAnim("action", "sing");
                    level.playSound(null, bug.blockPosition(), bug.pendingNote.value(), SoundSource.NEUTRAL, 0.8f, bug.notePitch);
                    if (bug.home != null) bug.getNavigation().moveTo(bug.home.getX() + 0.5, bug.home.getY(), bug.home.getZ() + 0.5, 1.0);
                    bug.pendingNote = null;
                }
            }
            default -> {
            }
        }
    }

    private static boolean isShiny(ItemStack stack) {
        return stack.is(Items.GOLD_INGOT) || stack.is(Items.GOLD_NUGGET) || stack.is(Items.DIAMOND) || stack.is(Items.EMERALD)
                || stack.is(Items.AMETHYST_SHARD) || stack.is(Items.GOLD_BLOCK) || stack.is(Items.DIAMOND_BLOCK);
    }

    private static boolean overheating(BugEntity bug) {
        BlockPos pos = bug.blockPosition();
        BlockState below = bug.level().getBlockState(pos.below());
        boolean cold = below.is(BlockTags.ICE) || below.is(Blocks.SNOW_BLOCK) || bug.level().getBlockState(pos).is(Blocks.SNOW)
                || bug.level().getBiome(pos).value().coldEnoughToSnow(pos);
        return !cold && (bug.level().getBiome(pos).value().getBaseTemperature() > 0.3f || bug.level().getBrightness(net.minecraft.world.level.LightLayer.BLOCK, pos) > 11);
    }

    private static void vanish(BugEntity bug, ParticleOptions particle) {
        ((ServerLevel) bug.level()).sendParticles(particle, bug.getX(), bug.getY() + 0.2, bug.getZ(), 5, 0.15, 0.15, 0.15, 0.01);
        bug.discard();
    }

    private static void burrow(BugEntity bug) {
        BlockState ground = bug.level().getBlockState(bug.blockPosition().below());
        ((ServerLevel) bug.level()).sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, ground),
                bug.getX(), bug.getY() + 0.1, bug.getZ(), 12, 0.2, 0.05, 0.2, 0.05);
        bug.playSound(SoundEvents.GRAVEL_BREAK, 0.5f, 1.3f);
        bug.discard();
    }

    private static void leapAway(BugEntity bug, Vec3 from) {
        Vec3 away = bug.position().subtract(from).multiply(1, 0, 1);
        if (away.lengthSqr() < 1.0E-4) away = new Vec3(bug.getRandom().nextDouble() - 0.5, 0, bug.getRandom().nextDouble() - 0.5);
        away = away.normalize();
        boolean spring = bug.species() == SPRINGTAIL;
        double power = spring ? 0.45 : 0.7;
        bug.setDeltaMovement(away.x * power, spring ? 0.65 : 0.5, away.z * power);
        bug.hasImpulse = true;
        bug.playSound(spring ? SoundEvents.SLIME_JUMP_SMALL : SoundEvents.SILVERFISH_STEP, 0.4f, 1.9f);
        bug.specialCooldown = spring ? 30 : 25;
    }

    private static void tickAntlion(BugEntity bug, ServerLevel level) {
        boolean onSand = level.getBlockState(bug.blockPosition().below()).is(BlockTags.SAND);
        boolean buried = onSand && bug.getNavigation().isDone();
        bug.setFlag(BugEntity.FLAG_HIDDEN, buried);
        // the pit only works while the antlion sits buried in it
        if (!buried || bug.tickCount % 5 != 0) return;
        for (LivingEntity e : level.getEntitiesOfClass(LivingEntity.class, bug.getBoundingBox().inflate(0.4, 0.3, 0.4), e -> e != bug)) {
            if (e instanceof Player p && (p.isCreative() || p.isSpectator())) continue;
            // wild prey only, and one per scan; a released pet is merely trapped like anything else
            if (e instanceof BugEntity other && isSmallPrey(other) && other.isAlive() && !other.isFromJar()) {
                bug.triggerAnim("action", "grab");
                level.sendParticles(ParticleTypes.ITEM_SLIME, other.getX(), other.getY(), other.getZ(), 4, 0.05, 0.05, 0.05, 0.02);
                other.discard();
                bug.heal(2);
                return;
            }
            if (bug.specialCooldown == 0) {
                if (com.bugslife.item.ChitinGear.bugProof(e)) continue;
                e.addEffect(new MobEffectInstance(MobEffects.MOVEMENT_SLOWDOWN, 40, 3), bug);
                Vec3 pull = bug.position().subtract(e.position()).scale(0.3);
                e.setDeltaMovement(e.getDeltaMovement().add(pull.x, -0.1, pull.z));
                e.hurtMarked = true;
                bug.triggerAnim("action", "grab");
                bug.playSound(SoundEvents.SAND_BREAK, 0.6f, 0.8f);
                bug.specialCooldown = 40;
            }
        }
    }

    private static void tickMoleCricket(BugEntity bug, ServerLevel level) {
        if (bug.hasFlag(BugEntity.FLAG_HIDDEN)) {
            if (--bug.specialTimer <= 0) resurface(bug, level);
            return;
        }
        if (bug.specialCooldown > 0 || bug.tickCount % 5 != 0) return;
        Player p = level.getNearestPlayer(bug, 4);
        boolean spooked = p != null && !p.isShiftKeyDown() && !p.isSpectator();
        if (spooked || bug.getRandom().nextInt(240) == 0) digDown(bug, level);
    }

    public static void digDown(BugEntity bug, ServerLevel level) {
        BlockState ground = level.getBlockState(bug.blockPosition().below());
        if (!(ground.is(BlockTags.DIRT) || ground.is(BlockTags.SAND))) return;
        bug.triggerAnim("action", "dig");
        level.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, ground), bug.getX(), bug.getY() + 0.1, bug.getZ(), 12, 0.2, 0.05, 0.2, 0.05);
        bug.playSound(SoundEvents.ROOTED_DIRT_BREAK, 0.6f, 1.2f);
        bug.setFlag(BugEntity.FLAG_HIDDEN, true);
        bug.setInvisible(true);
        bug.getNavigation().stop();
        bug.specialTimer = 60 + bug.getRandom().nextInt(80);
    }

    private static void resurface(BugEntity bug, ServerLevel level) {
        for (int i = 0; i < 16; i++) {
            BlockPos p = bug.blockPosition().offset(bug.getRandom().nextInt(13) - 6, bug.getRandom().nextInt(5) - 2, bug.getRandom().nextInt(13) - 6);
            if (level.getBlockState(p).isAir() && level.getBlockState(p.below()).is(BlockTags.DIRT)) {
                bug.moveTo(p.getX() + 0.5, p.getY(), p.getZ() + 0.5, bug.getRandom().nextFloat() * 360f, 0);
                break;
            }
        }
        BlockState ground = level.getBlockState(bug.blockPosition().below());
        level.sendParticles(new BlockParticleOption(ParticleTypes.BLOCK, ground), bug.getX(), bug.getY() + 0.1, bug.getZ(), 12, 0.2, 0.05, 0.2, 0.05);
        bug.setFlag(BugEntity.FLAG_HIDDEN, false);
        bug.setInvisible(false);
        bug.specialCooldown = 200;
    }

    private static void scatterPetals(BugEntity bug, ServerLevel level) {
        if (!canGrief(bug)) return;
        int petals = 0;
        BlockPos o = bug.blockPosition();
        for (BlockPos p : BlockPos.betweenClosed(o.offset(-5, -4, -5), o.offset(5, 2, 5))) {
            if (level.getBlockState(p).is(Blocks.PINK_PETALS)) petals++;
        }
        if (petals >= 10) return;
        for (int i = 0; i < 8; i++) {
            BlockPos ground = o.offset(bug.getRandom().nextInt(7) - 3, -bug.getRandom().nextInt(5), bug.getRandom().nextInt(7) - 3);
            if (level.getBlockState(ground).is(Blocks.GRASS_BLOCK) && level.getBlockState(ground.above()).isAir()) {
                level.setBlockAndUpdate(ground.above(), Blocks.PINK_PETALS.defaultBlockState());
                level.sendParticles(ParticleTypes.CHERRY_LEAVES, ground.getX() + 0.5, ground.getY() + 1.3, ground.getZ() + 0.5, 6, 0.3, 0.2, 0.3, 0);
                return;
            }
        }
    }

    private static void plantMushroom(BugEntity bug, ServerLevel level) {
        if (!canGrief(bug)) return;
        int shrooms = 0;
        BlockPos o = bug.blockPosition();
        for (BlockPos p : BlockPos.betweenClosed(o.offset(-4, -2, -4), o.offset(4, 2, 4))) {
            if (level.getBlockState(p).is(Blocks.RED_MUSHROOM) || level.getBlockState(p).is(Blocks.BROWN_MUSHROOM)) shrooms++;
        }
        if (shrooms >= 8) return;
        for (int i = 0; i < 8; i++) {
            BlockPos ground = o.offset(bug.getRandom().nextInt(5) - 2, bug.getRandom().nextInt(3) - 2, bug.getRandom().nextInt(5) - 2);
            if (level.getBlockState(ground).is(Blocks.MYCELIUM) && level.getBlockState(ground.above()).isAir()) {
                level.setBlockAndUpdate(ground.above(), (bug.getRandom().nextBoolean() ? Blocks.RED_MUSHROOM : Blocks.BROWN_MUSHROOM).defaultBlockState());
                level.sendParticles(ParticleTypes.MYCELIUM, ground.getX() + 0.5, ground.getY() + 1.1, ground.getZ() + 0.5, 6, 0.2, 0.1, 0.2, 0);
                return;
            }
        }
    }

    private static void chorusHop(BugEntity bug, ServerLevel level) {
        BlockPos o = bug.blockPosition();
        for (int i = 0; i < 20; i++) {
            BlockPos p = o.offset(bug.getRandom().nextInt(21) - 10, bug.getRandom().nextInt(7) - 3, bug.getRandom().nextInt(21) - 10);
            if (!level.getBlockState(p).is(Blocks.CHORUS_PLANT) && !level.getBlockState(p).is(Blocks.CHORUS_FLOWER)) continue;
            for (Direction d : Direction.Plane.HORIZONTAL) {
                BlockPos side = p.relative(d);
                if (level.getBlockState(side).isAir() && !level.getBlockState(side.below()).isAir()) {
                    level.sendParticles(ParticleTypes.PORTAL, bug.getX(), bug.getY() + 0.3, bug.getZ(), 16, 0.2, 0.3, 0.2, 0.3);
                    bug.teleportTo(side.getX() + 0.5, side.getY(), side.getZ() + 0.5);
                    level.playSound(null, side, SoundEvents.CHORUS_FRUIT_TELEPORT, SoundSource.NEUTRAL, 0.5f, 1.6f);
                    bug.specialCooldown = 200;
                    return;
                }
            }
        }
    }

    private static void gust(BugEntity bug, ServerLevel level, Player target) {
        Vec3 away = target.position().subtract(bug.position()).multiply(1, 0, 1);
        if (away.lengthSqr() < 1.0E-4) away = new Vec3(1, 0, 0);
        away = away.normalize();
        target.push(away.x * 1.4, 0.45, away.z * 1.4);
        target.hurtMarked = true;
        bug.triggerAnim("action", "gust");
        level.sendParticles(ParticleTypes.GUST, bug.getX(), bug.getY() + 0.3, bug.getZ(), 1, 0, 0, 0, 0);
        level.playSound(null, bug.blockPosition(), SoundEvents.BREEZE_WIND_CHARGE_BURST.value(), SoundSource.NEUTRAL, 0.7f, 1.4f);
        bug.specialCooldown = 60;
    }

    private static void stinkCloud(BugEntity bug) {
        if (bug.specialCooldown > 0) return;
        AreaEffectCloud cloud = new AreaEffectCloud(bug.level(), bug.getX(), bug.getY(), bug.getZ());
        cloud.setRadius(1.8f);
        cloud.setDuration(80);
        cloud.setRadiusPerTick(-0.01f);
        cloud.setParticle(ColorParticleOption.create(ParticleTypes.ENTITY_EFFECT, 0xFF8A9A3A));
        cloud.addEffect(new MobEffectInstance(MobEffects.CONFUSION, 160, 0));
        cloud.setOwner(bug);
        bug.level().addFreshEntity(cloud);
        bug.triggerAnim("action", "spray");
        bug.playSound(SoundEvents.PUFFER_FISH_BLOW_OUT, 0.6f, 1.5f);
        bug.specialCooldown = 100;
    }

    private static void clickJump(BugEntity bug) {
        bug.setDeltaMovement(bug.getDeltaMovement().add((bug.getRandom().nextDouble() - 0.5) * 0.3, 0.75, (bug.getRandom().nextDouble() - 0.5) * 0.3));
        bug.hasImpulse = true;
        bug.triggerAnim("action", "click");
        bug.playSound(SoundEvents.NOTE_BLOCK_HAT.value(), 1.0f, 0.7f);
        bug.playSound(SoundEvents.WOODEN_BUTTON_CLICK_ON, 1.0f, 1.8f);
    }

    private static void angerSwarm(BugEntity bug, LivingEntity attacker) {
        if (attacker instanceof Player p && (p.isCreative() || p.isSpectator())) return;
        for (BugEntity wasp : bug.level().getEntitiesOfClass(BugEntity.class, bug.getBoundingBox().inflate(12), b -> b.species() == PAPER_WASP)) {
            wasp.setTarget(attacker);
            wasp.specialTimer = 600;
        }
        bug.playSound(SoundEvents.BEE_LOOP_AGGRESSIVE, 1.0f, 1.3f);
    }

    // ================================================================== defences

    /** After the bug took damage (server). */
    public static void onHurt(BugEntity bug, DamageSource source) {
        LivingEntity attacker = source.getEntity() instanceof LivingEntity l ? l : null;
        switch (bug.species()) {
            case MILLIPEDE -> {
                if (attacker instanceof Player p && p.getMainHandItem().isEmpty()) {
                    p.addEffect(new MobEffectInstance(MobEffects.POISON, 80, 0), bug);
                }
            }
            case SCORPION -> {
                if (attacker != null) {
                    bug.triggerAnim("action", "sting");
                    attacker.addEffect(new MobEffectInstance(MobEffects.POISON, 100, 0), bug);
                }
            }
            case BOMBARDIER_BEETLE -> {
                if (attacker != null) spray(bug, attacker);
            }
            case STINK_BUG -> stinkCloud(bug);
            case PAPER_WASP -> {
                if (attacker != null) angerSwarm(bug, attacker);
            }
            case CLICK_BEETLE -> clickJump(bug);
            case EARWIG -> bug.triggerAnim("action", "pinch");
            case MOLE_CRICKET -> digDown(bug, (ServerLevel) bug.level());
            default -> {
            }
        }
    }

    private static void spray(BugEntity bug, LivingEntity target) {
        if (bug.specialCooldown > 0) return;
        if (!com.bugslife.item.ChitinGear.bugProof(target)) target.igniteForSeconds(2);
        bug.triggerAnim("action", "spray");
        ((ServerLevel) bug.level()).sendParticles(ParticleTypes.POOF, bug.getX(), bug.getY() + 0.2, bug.getZ(), 6, 0.1, 0.1, 0.1, 0.05);
        ((ServerLevel) bug.level()).sendParticles(ParticleTypes.SMALL_FLAME, bug.getX(), bug.getY() + 0.2, bug.getZ(), 4, 0.1, 0.1, 0.1, 0.02);
        bug.playSound(SoundEvents.FIRECHARGE_USE, 0.5f, 1.8f);
        bug.specialCooldown = 60;
    }

    /** A net swing missed this bug (server). */
    public static void onStartle(BugEntity bug, Player player) {
        switch (bug.species()) {
            case STINK_BUG -> stinkCloud(bug);
            case BOMBARDIER_BEETLE -> spray(bug, player);
            case CLICK_BEETLE -> clickJump(bug);
            case SPRINGTAIL, GRASSHOPPER -> leapAway(bug, player.position());
            case MOLE_CRICKET -> digDown(bug, (ServerLevel) bug.level());
            case PAPER_WASP -> angerSwarm(bug, player);
            case SCORPION -> {
                bug.triggerAnim("action", "sting");
                player.addEffect(new MobEffectInstance(MobEffects.POISON, 60, 0), bug);
            }
            case GUST_MOTH -> gust(bug, (ServerLevel) bug.level(), player);
            default -> {
            }
        }
    }

    /** Whether a net can reach the bug right now. */
    public static boolean catchable(BugEntity bug) {
        return !(bug.species() == MOLE_CRICKET && bug.hasFlag(BugEntity.FLAG_HIDDEN));
    }

    // ================================================================== interactions

    @Nullable
    public static InteractionResult interact(BugEntity bug, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        switch (bug.species()) {
            case HONEYPOT_ANT -> {
                if (!stack.is(Items.GLASS_BOTTLE)) return null;
                if (bug.level().isClientSide) return InteractionResult.SUCCESS;
                if (bug.specialCooldown > 0) {
                    player.displayClientMessage(Component.translatable("bugslife.msg.honeypot_empty").withStyle(ChatFormatting.GRAY), true);
                    return InteractionResult.CONSUME;
                }
                player.setItemInHand(hand, ItemUtils.createFilledResult(stack, player, new ItemStack(Items.HONEY_BOTTLE)));
                bug.playSound(SoundEvents.BOTTLE_FILL, 0.8f, 1.2f);
                bug.specialCooldown = 2400;
                if (player instanceof ServerPlayer sp) ModTriggers.BUG_ACTION.get().trigger(sp, "milk_honeypot");
                return InteractionResult.CONSUME;
            }
            case DARKLING_BEETLE -> {
                if (!stack.is(Items.GLASS_BOTTLE) || !bug.hasFlag(BugEntity.FLAG_ALERT)) return null;
                if (bug.level().isClientSide) return InteractionResult.SUCCESS;
                if (bug.specialCooldown > 0) return InteractionResult.CONSUME;
                player.setItemInHand(hand, ItemUtils.createFilledResult(stack, player,
                        net.minecraft.world.item.alchemy.PotionContents.createItemStack(Items.POTION, net.minecraft.world.item.alchemy.Potions.WATER)));
                bug.playSound(SoundEvents.BOTTLE_FILL, 0.8f, 1.4f);
                bug.specialCooldown = 1200;
                return InteractionResult.CONSUME;
            }
            case TARANTULA -> {
                if (bug.owner == null && (stack.is(ModItems.CRUNCHY_GRUB.get()) || stack.is(ModItems.ROASTED_GRUB.get()))) {
                    if (bug.level().isClientSide) return InteractionResult.SUCCESS;
                    if (!player.getAbilities().instabuild) stack.shrink(1);
                    ServerLevel level = (ServerLevel) bug.level();
                    if (bug.getRandom().nextInt(3) == 0) {
                        bug.owner = player.getUUID();
                        bug.setFromJar(true);
                        level.sendParticles(ParticleTypes.HEART, bug.getX(), bug.getY() + 0.5, bug.getZ(), 5, 0.2, 0.2, 0.2, 0);
                        if (player instanceof ServerPlayer sp) ModTriggers.BUG_ACTION.get().trigger(sp, "tame_tarantula");
                    } else {
                        level.sendParticles(ParticleTypes.SMOKE, bug.getX(), bug.getY() + 0.5, bug.getZ(), 5, 0.2, 0.2, 0.2, 0);
                    }
                    return InteractionResult.CONSUME;
                }
                if (player.getUUID().equals(bug.owner) && stack.isEmpty() && player.isShiftKeyDown()) {
                    if (!bug.level().isClientSide) {
                        bug.sitting = !bug.sitting;
                        player.displayClientMessage(Component.translatable(bug.sitting ? "bugslife.msg.tarantula_sit" : "bugslife.msg.tarantula_follow"), true);
                    }
                    return InteractionResult.sidedSuccess(bug.level().isClientSide);
                }
                return null;
            }
            default -> {
                return null;
            }
        }
    }

    // ================================================================== looks

    /** Glow strength override for expansion bugs, or -1 to use the default. */
    public static float glowStrength(BugEntity bug, float partialTick) {
        float t = bug.tickCount + partialTick;
        boolean night = !bug.level().isDay();
        return switch (bug.species()) {
            case SCORPION -> night ? 1.0f : 0.0f;
            case MORPHO -> bug.onGround() ? 0.2f : 0.25f + 0.75f * Math.abs(Mth.sin(t * 0.9f));
            case LUNA_MOTH -> night ? 0.6f + 0.25f * Mth.sin(t * 0.1f) : 0.15f;
            case CLICK_BEETLE -> 0.8f + 0.2f * Mth.sin(t * 0.3f);
            case STORM_BEETLE -> bug.hasFlag(BugEntity.FLAG_ALERT) ? 0.5f + 0.5f * (bug.getRandom().nextFloat()) : 0.25f;
            case SOUL_MOTH -> 0.75f + 0.25f * Mth.sin(t * 0.7f + Mth.sin(t * 0.23f) * 3);
            case ECHO_MOTH -> 0.4f + 0.6f * Math.max(0, Mth.sin(t * 0.08f));
            case CRYSTAL_BEETLE -> 0.6f + 0.4f * Mth.sin(t * 0.15f);
            default -> -1f;
        };
    }

    /** Client-side ambient particles. */
    public static void clientTick(BugEntity bug) {
        var random = bug.getRandom();
        ParticleOptions particle = null;
        int chance = 0;
        switch (bug.species()) {
            case SOUL_MOTH -> { particle = ParticleTypes.SOUL_FIRE_FLAME; chance = 12; }
            case DIVING_BEETLE -> { if (bug.isInWater()) { particle = ParticleTypes.BUBBLE; chance = 8; } }
            case BOOKWORM -> { particle = ParticleTypes.ENCHANT; chance = 25; }
            case SAKURA_MOTH -> { if (!bug.onGround()) { particle = ParticleTypes.CHERRY_LEAVES; chance = 20; } }
            case CRYSTAL_BEETLE -> { particle = ParticleTypes.GLOW; chance = 20; }
            case STORM_BEETLE -> { if (bug.hasFlag(BugEntity.FLAG_ALERT)) { particle = ParticleTypes.ELECTRIC_SPARK; chance = 3; } }
            case GUST_MOTH -> { particle = ParticleTypes.SMALL_GUST; chance = 40; }
            case ICE_CRAWLER -> { particle = ParticleTypes.SNOWFLAKE; chance = 40; }
            case ECHO_MOTH -> { particle = ParticleTypes.SCULK_CHARGE_POP; chance = 30; }
            case SHULKER_MITE -> { particle = ParticleTypes.END_ROD; chance = 30; }
            default -> {
            }
        }
        if (particle != null && random.nextInt(chance) == 0) {
            bug.level().addParticle(particle, bug.getRandomX(0.5), bug.getY() + bug.getBbHeight() * random.nextDouble(), bug.getRandomZ(0.5),
                    (random.nextDouble() - 0.5) * 0.02, 0.02, (random.nextDouble() - 0.5) * 0.02);
        }
    }

    // ================================================================== world events

    /** Katydids answer a note block: they sing the same note back and come closer. */
    @SubscribeEvent
    public static void onNoteBlock(NoteBlockEvent.Play event) {
        if (!(event.getLevel() instanceof ServerLevel level)) return;
        BlockPos pos = event.getPos();
        Holder<SoundEvent> sound = event.getInstrument().getSoundEvent();
        float pitch = NoteBlock.getPitchFromNote(event.getVanillaNoteId());
        boolean answered = false;
        for (BugEntity bug : level.getEntitiesOfClass(BugEntity.class, new AABB(pos).inflate(16), b -> b.species() == KATYDID)) {
            bug.pendingNote = sound;
            bug.notePitch = pitch;
            bug.home = pos.immutable();
            bug.specialTimer = 8 + bug.getRandom().nextInt(16);
            answered = true;
        }
        if (answered) {
            for (ServerPlayer p : level.getEntitiesOfClass(ServerPlayer.class, new AABB(pos).inflate(16))) {
                ModTriggers.BUG_ACTION.get().trigger(p, "katydid_duet");
            }
        }
    }

    /** Echo moths swallow vibrations: sculk sensors, shriekers and wardens cannot hear anything near one. */
    @SubscribeEvent
    public static void onVibration(VanillaGameEvent event) {
        if (ECHO_MOTHS.isEmpty() || event.getLevel().isClientSide) return;
        Vec3 at = event.getEventPosition();
        ECHO_MOTHS.removeIf(m -> m.isRemoved() || !m.isAlive());
        for (BugEntity moth : ECHO_MOTHS) {
            if (moth.level() == event.getLevel() && moth.distanceToSqr(at) < 64 && event.getCause() != moth) {
                event.setCanceled(true);
                return;
            }
        }
    }

    /** Phantoms will not pick a target near an owl butterfly. */
    @SubscribeEvent
    public static void onTarget(LivingChangeTargetEvent event) {
        if (!(event.getEntity() instanceof Phantom) || event.getNewAboutToBeSetTarget() == null || OWL_BUTTERFLIES.isEmpty()) return;
        LivingEntity target = event.getNewAboutToBeSetTarget();
        OWL_BUTTERFLIES.removeIf(m -> m.isRemoved() || !m.isAlive());
        for (BugEntity owl : OWL_BUTTERFLIES) {
            if (owl.level() == target.level() && owl.distanceToSqr(target) < 24 * 24) {
                event.setCanceled(true);
                if (target instanceof ServerPlayer sp) ModTriggers.BUG_ACTION.get().trigger(sp, "owl_scare");
                return;
            }
        }
    }
}
