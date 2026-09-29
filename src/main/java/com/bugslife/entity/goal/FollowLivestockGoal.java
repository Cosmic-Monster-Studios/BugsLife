package com.bugslife.entity.goal;

import com.bugslife.entity.BugEntity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.animal.Cow;
import net.minecraft.world.entity.animal.Pig;
import net.minecraft.world.entity.animal.Sheep;
import net.minecraft.world.entity.animal.goat.Goat;
import net.minecraft.world.entity.animal.horse.AbstractHorse;

import java.util.EnumSet;
import java.util.List;

/** Dung beetles trundle after grazing animals, rolling their ball along. */
public class FollowLivestockGoal extends Goal {
    private final BugEntity bug;
    private LivingEntity target;

    public FollowLivestockGoal(BugEntity bug) {
        this.bug = bug;
        setFlags(EnumSet.of(Flag.MOVE));
    }

    public static boolean isLivestock(LivingEntity e) {
        return e instanceof Cow || e instanceof Sheep || e instanceof Pig || e instanceof Goat || e instanceof AbstractHorse;
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }

    @Override
    public boolean canUse() {
        if (bug.getRandom().nextInt(40) != 0 || bug.getRandom().nextInt(3) != 0) return false;
        List<LivingEntity> near = bug.level().getEntitiesOfClass(LivingEntity.class, bug.getBoundingBox().inflate(16), FollowLivestockGoal::isLivestock);
        LivingEntity best = null;
        double bestDist = Double.MAX_VALUE;
        for (LivingEntity e : near) {
            double d = e.distanceToSqr(bug);
            if (d < bestDist) {
                bestDist = d;
                best = e;
            }
        }
        if (best == null || bestDist < 25) return false;
        target = best;
        return true;
    }

    @Override
    public boolean canContinueToUse() {
        return target != null && target.isAlive() && !bug.getNavigation().isDone() && target.distanceToSqr(bug) > 9;
    }

    @Override
    public void start() {
        bug.getNavigation().moveTo(target, 0.9);
    }

    @Override
    public void stop() {
        target = null;
    }
}
