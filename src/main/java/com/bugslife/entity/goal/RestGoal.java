package com.bugslife.entity.goal;

import com.bugslife.entity.BugEntity;
import net.minecraft.world.entity.ai.goal.Goal;

import java.util.EnumSet;

/**
 * Flying bugs land and rest: fireflies and moths through the day, butterflies and dragonflies through the night,
 * and every flyer now and then for a breather.
 */
public class RestGoal extends Goal {
    private final BugEntity bug;
    private int restTicks;
    private boolean landed;

    public RestGoal(BugEntity bug) {
        this.bug = bug;
        setFlags(EnumSet.of(Flag.MOVE, Flag.JUMP));
    }

    private boolean restingTime() {
        boolean day = bug.level().isDay();
        return switch (bug.species()) {
            case FIREFLY, SILK_MOTH -> day;
            case MONARCH, DRAGONFLY -> !day;
            default -> false;
        };
    }

    @Override
    public boolean canUse() {
        if (bug.isStartled()) return false;
        return bug.getRandom().nextInt(restingTime() ? 20 : 500) == 0;
    }

    @Override
    public boolean canContinueToUse() {
        return restTicks > 0 && !bug.isStartled();
    }

    @Override
    public void start() {
        restTicks = restingTime() ? 1200 : 100 + bug.getRandom().nextInt(300);
        landed = false;
        int ground = BugFlyGoal.groundBelow(bug.level(), bug.getBlockX(), bug.getBlockY(), bug.getBlockZ());
        bug.getNavigation().moveTo(bug.getX(), ground + 1.0, bug.getZ(), 0.8);
    }

    @Override
    public void tick() {
        if (!landed) {
            if (bug.onGround() || bug.getNavigation().isDone()) {
                landed = true;
                bug.getNavigation().stop();
                bug.setNoGravity(false);
                bug.setFlag(BugEntity.FLAG_PERCHED, true);
            }
            return;
        }
        restTicks--;
        bug.getNavigation().stop();
    }

    @Override
    public void stop() {
        bug.setFlag(BugEntity.FLAG_PERCHED, false);
        restTicks = 0;
    }
}
