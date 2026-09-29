package com.bugslife.entity.goal;

import com.bugslife.entity.BugEntity;
import com.bugslife.registry.ModTriggers;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.FlowerBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import org.jetbrains.annotations.Nullable;

import java.util.EnumSet;

/** Butterflies visit flowers, perch on them to sip nectar, and now and then spread them to nearby grass. */
public class FlowerVisitGoal extends Goal {
    private final BugEntity bug;
    /** Hawk-moths hover in front of the flower instead of landing on it. */
    private final boolean hover;
    private BlockPos flower;
    private int perchTicks;
    private int timeout;

    public FlowerVisitGoal(BugEntity bug) {
        this(bug, false);
    }

    public FlowerVisitGoal(BugEntity bug, boolean hover) {
        this.bug = bug;
        this.hover = hover;
        setFlags(EnumSet.of(Flag.MOVE));
    }

    @Override
    public boolean canUse() {
        if (!bug.level().isDay() || bug.isStartled() || bug.getRandom().nextInt(100) != 0) return false;
        flower = findFlower();
        return flower != null;
    }

    @Override
    public boolean canContinueToUse() {
        return flower != null && timeout > 0 && !bug.isStartled() && bug.level().getBlockState(flower).is(BlockTags.FLOWERS);
    }

    @Override
    public void start() {
        perchTicks = 0;
        timeout = 600;
        bug.getNavigation().moveTo(flower.getX() + 0.5, flower.getY() + 0.7, flower.getZ() + 0.5, 1.0);
    }

    @Override
    public void tick() {
        timeout--;
        if (perchTicks == 0) {
            if (bug.distanceToSqr(flower.getX() + 0.5, flower.getY() + 0.5, flower.getZ() + 0.5) < 1.5) {
                perchTicks = hover ? 40 + bug.getRandom().nextInt(60) : 120 + bug.getRandom().nextInt(200);
                bug.getNavigation().stop();
                if (!hover) {
                    bug.setNoGravity(false);
                    bug.setFlag(BugEntity.FLAG_PERCHED, true);
                }
            } else if (bug.getNavigation().isDone()) {
                bug.getNavigation().moveTo(flower.getX() + 0.5, flower.getY() + 0.7, flower.getZ() + 0.5, 1.0);
            }
            return;
        }
        bug.getNavigation().stop();
        if (hover) {
            // hold station in front of the bloom, proboscis in the flower
            bug.getMoveControl().setWantedPosition(flower.getX() + 0.5, flower.getY() + 0.6, flower.getZ() + 0.5, 0.6);
            bug.getLookControl().setLookAt(flower.getX() + 0.5, flower.getY() + 0.3, flower.getZ() + 0.5);
        }
        if (--perchTicks <= 0) {
            timeout = 0;
        } else if (bug.getRandom().nextInt(240) == 0) {
            pollinate();
        }
    }

    @Override
    public void stop() {
        bug.setFlag(BugEntity.FLAG_PERCHED, false);
        flower = null;
    }

    @Nullable
    private BlockPos findFlower() {
        BlockPos origin = bug.blockPosition();
        BlockPos best = null;
        double bestDist = Double.MAX_VALUE;
        for (BlockPos p : BlockPos.betweenClosed(origin.offset(-8, -4, -8), origin.offset(8, 3, 8))) {
            if (bug.level().getBlockState(p).is(BlockTags.FLOWERS)) {
                double d = p.distSqr(origin);
                if (d < bestDist) {
                    bestDist = d;
                    best = p.immutable();
                }
            }
        }
        return best;
    }

    private void pollinate() {
        if (!(bug.level() instanceof ServerLevel level)) return;
        BlockState state = level.getBlockState(flower);
        if (!(state.getBlock() instanceof FlowerBlock)) return;
        int nearby = 0;
        for (BlockPos p : BlockPos.betweenClosed(flower.offset(-4, -2, -4), flower.offset(4, 2, 4))) {
            if (level.getBlockState(p).is(BlockTags.FLOWERS)) nearby++;
        }
        if (nearby > 14) return;
        for (int i = 0; i < 8; i++) {
            BlockPos ground = flower.offset(bug.getRandom().nextInt(7) - 3, bug.getRandom().nextInt(3) - 1, bug.getRandom().nextInt(7) - 3);
            BlockPos spot = ground.above();
            if (level.getBlockState(ground).is(Blocks.GRASS_BLOCK) && level.getBlockState(spot).isAir()) {
                level.setBlockAndUpdate(spot, state);
                level.sendParticles(ParticleTypes.HAPPY_VILLAGER, spot.getX() + 0.5, spot.getY() + 0.4, spot.getZ() + 0.5, 5, 0.3, 0.3, 0.3, 0);
                level.sendParticles(ParticleTypes.FALLING_NECTAR, bug.getX(), bug.getY() + 0.3, bug.getZ(), 3, 0.1, 0.1, 0.1, 0);
                level.playSound(null, spot, SoundEvents.AZALEA_LEAVES_PLACE, SoundSource.BLOCKS, 0.6f, 1.4f);
                for (ServerPlayer player : level.getEntitiesOfClass(ServerPlayer.class, new AABB(spot).inflate(12))) {
                    ModTriggers.BUG_ACTION.get().trigger(player, "witness_pollinate");
                }
                return;
            }
        }
    }
}
