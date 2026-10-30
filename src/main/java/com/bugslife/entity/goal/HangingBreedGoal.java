package com.bugslife.entity.goal;

import com.bugslife.entity.BugEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.entity.animal.Animal;
import net.minecraft.world.entity.ai.goal.BreedGoal;

/** Hanging bugs court nearby partners without navigating away from their ceiling. */
public class HangingBreedGoal extends BreedGoal {
    private int courtshipTicks;

    public HangingBreedGoal(BugEntity bug) {
        super(bug, 0.0);
    }

    @Override
    public boolean canUse() {
        return super.canUse() && readyToBreed();
    }

    @Override
    public boolean canContinueToUse() {
        return readyToBreed() && courtshipTicks < adjustedTickDelay(60);
    }

    private boolean readyToBreed() {
        return partner != null && animal.isAlive() && partner.isAlive()
                && animal.level() == partner.level() && animal.canMate(partner)
                && !animal.isPanicking() && !partner.isPanicking()
                && animal.distanceToSqr(partner) < 9.0 && attached(animal) && attached(partner);
    }

    private static boolean attached(Animal bug) {
        BlockPos ceiling = BlockPos.containing(bug.getX(), bug.getBoundingBox().maxY + 0.05, bug.getZ());
        return bug.level().getBlockState(ceiling).isFaceSturdy(bug.level(), ceiling, Direction.DOWN);
    }

    @Override
    public void tick() {
        // A partner can be caught or lose its ceiling between the selector's full updates.
        if (!readyToBreed()) return;
        animal.getLookControl().setLookAt(partner, 10.0F, animal.getMaxHeadXRot());
        if (++courtshipTicks >= adjustedTickDelay(60)) breed();
    }

    @Override
    public void stop() {
        super.stop();
        courtshipTicks = 0;
    }
}
