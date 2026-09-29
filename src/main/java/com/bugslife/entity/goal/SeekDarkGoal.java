package com.bugslife.entity.goal;

import com.bugslife.entity.BugEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.level.Level;
import org.jetbrains.annotations.Nullable;

import java.util.EnumSet;

/** Earwigs hate light: in a bright spot they scuttle to the darkest nook they can find. */
public class SeekDarkGoal extends Goal {
    private final BugEntity bug;
    private BlockPos target;

    public SeekDarkGoal(BugEntity bug) {
        this.bug = bug;
        setFlags(EnumSet.of(Flag.MOVE));
    }

    private int light(BlockPos pos) {
        return bug.level().getMaxLocalRawBrightness(pos);
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }

    @Override
    public boolean canUse() {
        if (bug.getRandom().nextInt(20) != 0 || light(bug.blockPosition()) <= 7) return false;
        target = findDark();
        return target != null;
    }

    @Nullable
    private BlockPos findDark() {
        Level level = bug.level();
        BlockPos best = null;
        int bestLight = light(bug.blockPosition());
        for (int i = 0; i < 24; i++) {
            BlockPos p = bug.blockPosition().offset(bug.getRandom().nextInt(13) - 6, bug.getRandom().nextInt(5) - 2, bug.getRandom().nextInt(13) - 6);
            if (!level.getBlockState(p).isAir() || !level.getBlockState(p.below()).isSolid()) continue;
            int l = light(p);
            if (l < bestLight) {
                bestLight = l;
                best = p;
            }
        }
        return best;
    }

    @Override
    public boolean canContinueToUse() {
        return target != null && !bug.getNavigation().isDone();
    }

    @Override
    public void start() {
        bug.getNavigation().moveTo(target.getX() + 0.5, target.getY(), target.getZ() + 0.5, 1.4);
    }

    @Override
    public void stop() {
        target = null;
    }
}
