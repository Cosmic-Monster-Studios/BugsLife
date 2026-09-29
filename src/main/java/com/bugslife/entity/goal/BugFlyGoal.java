package com.bugslife.entity.goal;

import com.bugslife.bug.BugSpecies;
import com.bugslife.entity.BugEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;

import java.util.EnumSet;

/** Flutters between random spots a few blocks above the ground. Dragonflies stick close to water. */
public class BugFlyGoal extends Goal {
    private final BugEntity bug;

    public BugFlyGoal(BugEntity bug) {
        this.bug = bug;
        setFlags(EnumSet.of(Flag.MOVE));
    }

    @Override
    public boolean canUse() {
        int chance = bug.species() == BugSpecies.DRAGONFLY ? 4 : 10;
        return bug.getNavigation().isDone() && !bug.hasFlag(BugEntity.FLAG_PERCHED) && bug.getRandom().nextInt(chance) == 0;
    }

    @Override
    public boolean canContinueToUse() {
        return bug.getNavigation().isInProgress();
    }

    @Override
    public void start() {
        Vec3 target = findTarget();
        if (target != null) {
            double speed = bug.species() == BugSpecies.DRAGONFLY ? 1.6 : 1.0;
            bug.getNavigation().moveTo(target.x, target.y, target.z, speed);
        }
    }

    @Nullable
    private Vec3 findTarget() {
        Level level = bug.level();
        RandomSource random = bug.getRandom();
        boolean dragonfly = bug.species() == BugSpecies.DRAGONFLY;
        int range = dragonfly ? 12 : 8;
        for (int i = 0; i < 12; i++) {
            int x = bug.getBlockX() + random.nextInt(range * 2 + 1) - range;
            int z = bug.getBlockZ() + random.nextInt(range * 2 + 1) - range;
            int ground = groundBelow(level, x, bug.getBlockY() + 4, z);
            BlockPos pos = new BlockPos(x, ground + 1 + random.nextInt(dragonfly ? 3 : 4), z);
            if (!level.getBlockState(pos).isAir() || !level.getFluidState(pos).isEmpty()) continue;
            if (dragonfly && i < 9 && !nearWater(level, pos)) continue;
            return Vec3.atCenterOf(pos);
        }
        return null;
    }

    /** Y of the first non-air block at or below startY in this column (within 16 blocks). */
    static int groundBelow(Level level, int x, int startY, int z) {
        BlockPos.MutableBlockPos pos = new BlockPos.MutableBlockPos(x, startY, z);
        for (int i = 0; i < 16; i++) {
            if (!level.getBlockState(pos).isAir() || !level.getFluidState(pos).isEmpty()) {
                return pos.getY();
            }
            pos.move(0, -1, 0);
        }
        return startY - 6;
    }

    private static boolean nearWater(Level level, BlockPos pos) {
        for (BlockPos p : BlockPos.betweenClosed(pos.offset(-3, -4, -3), pos.offset(3, 0, 3))) {
            if (level.getFluidState(p).is(FluidTags.WATER)) return true;
        }
        return false;
    }
}
