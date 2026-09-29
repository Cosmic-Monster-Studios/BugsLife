package com.bugslife.entity.goal;

import com.bugslife.entity.BugEntity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.animal.Cow;
import net.minecraft.world.entity.animal.Fox;
import net.minecraft.world.entity.animal.Pig;
import net.minecraft.world.entity.animal.Sheep;
import net.minecraft.world.entity.animal.Wolf;
import net.minecraft.world.entity.animal.goat.Goat;
import net.minecraft.world.entity.animal.horse.AbstractHorse;

import java.util.EnumSet;
import java.util.List;

/** Ticks wait in long grass for a passing animal, climb aboard, and ride it around for a while. */
public class RideAnimalGoal extends Goal {
    private final BugEntity tick;
    private LivingEntity host;
    private int ticks;

    public RideAnimalGoal(BugEntity tick) {
        this.tick = tick;
        setFlags(EnumSet.of(Flag.MOVE));
    }

    public static boolean isHost(LivingEntity e) {
        return e instanceof Cow || e instanceof Sheep || e instanceof Pig || e instanceof Wolf || e instanceof Fox
                || e instanceof Goat || e instanceof AbstractHorse;
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }

    @Override
    public boolean canUse() {
        if (tick.isPassenger() || tick.isFromJar() || tick.isStartled() || tick.getRandom().nextInt(20) != 0) return false;
        List<LivingEntity> near = tick.level().getEntitiesOfClass(LivingEntity.class, tick.getBoundingBox().inflate(4),
                e -> isHost(e) && e.getPassengers().isEmpty());
        host = near.isEmpty() ? null : near.get(0);
        return host != null;
    }

    @Override
    public boolean canContinueToUse() {
        return host != null && host.isAlive() && !tick.isPassenger() && ticks > 0;
    }

    @Override
    public void start() {
        ticks = 200;
    }

    @Override
    public void tick() {
        ticks--;
        if (tick.distanceToSqr(host) < 1.6) {
            tick.startRiding(host, true);
            tick.specialTimer = 1200 + tick.getRandom().nextInt(2400);
        } else if (tick.tickCount % 10 == 0) {
            tick.getNavigation().moveTo(host, 1.2);
        }
    }

    @Override
    public void stop() {
        host = null;
    }
}
