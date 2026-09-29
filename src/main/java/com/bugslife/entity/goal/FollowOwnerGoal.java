package com.bugslife.entity.goal;

import com.bugslife.entity.BugEntity;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.player.Player;

import java.util.EnumSet;

/** A tamed tarantula ambles after its owner, and catches up by teleporting if left far behind. */
public class FollowOwnerGoal extends Goal {
    private final BugEntity pet;
    private Player owner;

    public FollowOwnerGoal(BugEntity pet) {
        this.pet = pet;
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }

    @Override
    public boolean canUse() {
        if (pet.owner == null || pet.sitting) return false;
        owner = pet.level().getPlayerByUUID(pet.owner);
        return owner != null && !owner.isSpectator() && pet.distanceToSqr(owner) > 16;
    }

    @Override
    public boolean canContinueToUse() {
        return owner != null && !pet.sitting && pet.distanceToSqr(owner) > 5;
    }

    @Override
    public void tick() {
        pet.getLookControl().setLookAt(owner, 10f, pet.getMaxHeadXRot());
        if (pet.distanceToSqr(owner) > 400) {
            pet.moveTo(owner.getX(), owner.getY(), owner.getZ(), pet.getYRot(), pet.getXRot());
            pet.getNavigation().stop();
        } else if (pet.tickCount % 10 == 0) {
            pet.getNavigation().moveTo(owner, 1.3);
        }
    }

    @Override
    public void stop() {
        owner = null;
        pet.getNavigation().stop();
    }
}
