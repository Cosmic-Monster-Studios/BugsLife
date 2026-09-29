package com.bugslife.entity.goal;

import com.bugslife.bug.BugSpecies;
import com.bugslife.entity.BugEntity;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.ai.goal.Goal;

import java.util.EnumSet;
import java.util.List;

/** Two stag beetles that meet square off and wrestle with their antler-like jaws. */
public class SparGoal extends Goal {
    private final BugEntity bug;
    private BugEntity rival;
    private int ticks;
    private int cooldown;

    public SparGoal(BugEntity bug) {
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
        if (bug.isBaby() || bug.isClinging() || bug.getRandom().nextInt(120) != 0) return false;
        List<BugEntity> others = bug.level().getEntitiesOfClass(BugEntity.class, bug.getBoundingBox().inflate(4),
                b -> b != bug && b.species() == BugSpecies.STAG_BEETLE && !b.isBaby());
        rival = others.isEmpty() ? null : others.get(0);
        return rival != null;
    }

    @Override
    public boolean canContinueToUse() {
        return rival != null && rival.isAlive() && ticks > 0 && !bug.isStartled();
    }

    @Override
    public void start() {
        ticks = 80;
        bug.getNavigation().moveTo(rival, 0.8);
    }

    @Override
    public void tick() {
        ticks--;
        bug.getLookControl().setLookAt(rival);
        rival.getLookControl().setLookAt(bug);
        if (bug.distanceToSqr(rival) < 1.0) {
            bug.getNavigation().stop();
            rival.getNavigation().stop();
        }
        if (ticks % 12 == 0) {
            bug.triggerAnim("action", "spar");
            rival.triggerAnim("action", "spar");
            bug.playSound(SoundEvents.ARMOR_EQUIP_TURTLE.value(), 0.25f, 1.8f);
        }
    }

    @Override
    public void stop() {
        rival = null;
        cooldown = 800;
    }
}
