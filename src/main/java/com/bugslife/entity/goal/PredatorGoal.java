package com.bugslife.entity.goal;

import com.bugslife.entity.BugEntity;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;
import java.util.List;
import java.util.function.Predicate;

/**
 * A bug that eats other bugs. Three hunting styles:
 * STALK walks up and bites (orb weaver at its web), POUNCE leaps from a few blocks away (jumping spider),
 * AMBUSH never moves and strikes anything that wanders into reach (praying mantis).
 */
public class PredatorGoal extends Goal {
    public enum Style { STALK, POUNCE, AMBUSH }

    private final BugEntity bug;
    private final Predicate<BugEntity> prey;
    private final Style style;
    private final double range;
    private BugEntity target;
    private int cooldown;
    private int ticks;

    public PredatorGoal(BugEntity bug, Style style, double range, Predicate<BugEntity> prey) {
        this.bug = bug;
        this.style = style;
        this.range = range;
        this.prey = prey;
        setFlags(style == Style.AMBUSH ? EnumSet.of(Flag.LOOK) : EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }

    @Override
    public boolean canUse() {
        if (cooldown > 0) {
            cooldown--;
            return false;
        }
        if (bug.isBaby() || bug.isClinging() || bug.getRandom().nextInt(10) != 0) return false;
        List<BugEntity> near = bug.level().getEntitiesOfClass(BugEntity.class, bug.getBoundingBox().inflate(range),
                b -> b != bug && b.isAlive() && !b.isFromJar() && prey.test(b));
        target = near.isEmpty() ? null : near.get(0);
        return target != null;
    }

    @Override
    public boolean canContinueToUse() {
        return target != null && target.isAlive() && ticks > 0 && bug.distanceToSqr(target) < (range + 2) * (range + 2);
    }

    @Override
    public void start() {
        ticks = 200;
        if (style == Style.STALK) bug.getNavigation().moveTo(target, 1.2);
    }

    @Override
    public void tick() {
        // tick() also runs on the ticks where canContinueToUse() is not re-checked (requiresUpdateEveryTick),
        // so the prey may already be eaten, caught or despawned here
        if (target == null || !target.isAlive()) {
            ticks = 0;
            return;
        }
        ticks--;
        bug.getLookControl().setLookAt(target);
        double dist = bug.distanceToSqr(target);
        switch (style) {
            case STALK -> {
                if (bug.tickCount % 10 == 0) bug.getNavigation().moveTo(target, 1.2);
            }
            case POUNCE -> {
                if (bug.onGround() && dist < 9 && dist > 0.8 && bug.tickCount % 15 == 0) {
                    Vec3 dir = target.position().subtract(bug.position());
                    bug.setDeltaMovement(dir.x * 0.25, 0.35, dir.z * 0.25);
                    bug.hasImpulse = true;
                } else if (dist >= 9 && bug.tickCount % 10 == 0) {
                    bug.getNavigation().moveTo(target, 1.0);
                }
            }
            case AMBUSH -> {
                if (dist > range * range) ticks = 0;
            }
        }
        if (dist < (style == Style.AMBUSH ? 3.0 : 0.7)) {
            eat();
        }
    }

    private void eat() {
        if (bug.species().actionAnim() != null) {
            bug.triggerAnim("action", bug.species().actionAnim());
        }
        if (bug.level() instanceof ServerLevel level) {
            level.sendParticles(ParticleTypes.ITEM_SLIME, target.getX(), target.getY() + 0.1, target.getZ(), 4, 0.05, 0.05, 0.05, 0.02);
        }
        bug.playSound(SoundEvents.GENERIC_EAT, 0.3f, 1.8f);
        target.discard();
        bug.heal(2.0f);
        target = null;
        cooldown = 900;
    }

    @Override
    public void stop() {
        target = null;
        if (style != Style.AMBUSH) bug.getNavigation().stop();
    }
}
