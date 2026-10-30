package com.bugslife.entity.goal;

import com.bugslife.entity.BugEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;

import java.util.EnumSet;
import java.util.function.Predicate;

/** Walks to the foot of a favourite kind of tree, then crawls up the bark and sits there a while. */
public class ClingGoal extends Goal {
    private final BugEntity bug;
    private final Predicate<BlockState> bark;
    private BlockPos stand;
    private Direction face;
    private int ticks;

    public ClingGoal(BugEntity bug, Predicate<BlockState> bark) {
        this.bug = bug;
        this.bark = bark;
        setFlags(EnumSet.of(Flag.MOVE));
    }

    @Override
    public boolean canUse() {
        if (bug.isClinging() || bug.isStartled() || !bug.onGround() || bug.getRandom().nextInt(60) != 0) return false;
        return findTrunk();
    }

    private boolean findTrunk() {
        Level level = bug.level();
        RandomSource random = bug.getRandom();
        BlockPos origin = bug.blockPosition();
        double best = Double.MAX_VALUE;
        stand = null;
        for (BlockPos p : BlockPos.betweenClosed(origin.offset(-6, -1, -6), origin.offset(6, 1, 6))) {
            if (!bark.test(level.getBlockState(p))) continue;
            for (Direction d : Direction.Plane.HORIZONTAL) {
                BlockPos s = p.relative(d);
                if (level.getBlockState(s).isAir() && level.getBlockState(s.below()).isFaceSturdy(level, s.below(), Direction.UP)) {
                    // a little randomness so bugs don't all pick the same side
                    double dist = s.distSqr(origin) + random.nextDouble() * 4;
                    if (dist < best) {
                        best = dist;
                        stand = s.immutable();
                        face = d.getOpposite();
                    }
                }
            }
        }
        return stand != null;
    }

    @Override
    public boolean canContinueToUse() {
        return stand != null && ticks > 0 && !bug.isClinging();
    }

    @Override
    public void start() {
        ticks = 300;
        bug.getNavigation().moveTo(stand.getX() + 0.5, stand.getY(), stand.getZ() + 0.5, 1.0);
    }

    @Override
    public void tick() {
        if (stand == null) {
            return;
        }
        ticks--;
        double dx = bug.getX() - (stand.getX() + 0.5);
        double dz = bug.getZ() - (stand.getZ() + 0.5);
        if (dx * dx + dz * dz < 0.36 && Math.abs(bug.getY() - stand.getY()) < 0.6) {
            bug.startCling(face, 1.0 + bug.getRandom().nextDouble() * 2.5, 400 + bug.getRandom().nextInt(900));
            stand = null;
        } else if (bug.getNavigation().isDone()) {
            bug.getNavigation().moveTo(stand.getX() + 0.5, stand.getY(), stand.getZ() + 0.5, 1.0);
        }
    }

    @Override
    public void stop() {
        stand = null;
    }
}
