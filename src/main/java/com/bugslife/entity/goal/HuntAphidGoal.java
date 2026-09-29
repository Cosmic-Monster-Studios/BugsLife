package com.bugslife.entity.goal;

import com.bugslife.bug.BugSpecies;
import com.bugslife.entity.BugEntity;
import com.bugslife.registry.ModTriggers;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.ai.goal.Goal;

import java.util.EnumSet;
import java.util.List;

/** Ladybugs hunt aphids - a natural pest control. */
public class HuntAphidGoal extends Goal {
    private final BugEntity bug;
    private BugEntity prey;
    private int cooldown;
    private int ticks;

    public HuntAphidGoal(BugEntity bug) {
        this.bug = bug;
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
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
        if (bug.isBaby() || bug.isClinging() || bug.getRandom().nextInt(40) != 0) return false;
        List<BugEntity> aphids = bug.level().getEntitiesOfClass(BugEntity.class, bug.getBoundingBox().inflate(8),
                b -> b.species() == BugSpecies.APHID && !b.isFromJar());
        prey = aphids.isEmpty() ? null : aphids.get(bug.getRandom().nextInt(aphids.size()));
        return prey != null;
    }

    @Override
    public boolean canContinueToUse() {
        return prey != null && prey.isAlive() && ticks > 0;
    }

    @Override
    public void start() {
        ticks = 240;
        bug.getNavigation().moveTo(prey, 1.25);
    }

    @Override
    public void tick() {
        ticks--;
        bug.getLookControl().setLookAt(prey);
        if (bug.distanceToSqr(prey) < 0.6) {
            if (bug.level() instanceof ServerLevel level) {
                level.sendParticles(ParticleTypes.ITEM_SLIME, prey.getX(), prey.getY() + 0.1, prey.getZ(), 4, 0.05, 0.05, 0.05, 0.02);
                bug.playSound(SoundEvents.GENERIC_EAT, 0.3f, 2.0f);
                for (ServerPlayer player : level.getEntitiesOfClass(ServerPlayer.class, bug.getBoundingBox().inflate(10))) {
                    ModTriggers.BUG_ACTION.get().trigger(player, "witness_hunt");
                }
            }
            prey.discard();
            bug.heal(1.0f);
            prey = null;
            cooldown = 1200;
        } else if (bug.tickCount % 10 == 0) {
            bug.getNavigation().moveTo(prey, 1.25);
        }
    }

    @Override
    public void stop() {
        prey = null;
        bug.getNavigation().stop();
    }
}
