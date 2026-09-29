package com.bugslife.entity.goal;

import com.bugslife.entity.BugEntity;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.phys.Vec3;

import java.util.EnumSet;

/** Whirligig beetles gyrate in tight, fast circles on the water - which is how they got their name. */
public class CircleSwimGoal extends Goal {
    private final BugEntity bug;
    private Vec3 center;
    private float angle;
    private int ticks;
    private int direction;

    public CircleSwimGoal(BugEntity bug) {
        this.bug = bug;
        setFlags(EnumSet.of(Flag.MOVE));
    }

    @Override
    public boolean canUse() {
        return bug.isInWater() || bug.level().getFluidState(bug.blockPosition().below()).isSource()
                ? bug.getRandom().nextInt(20) == 0 : false;
    }

    @Override
    public boolean canContinueToUse() {
        return ticks > 0 && !bug.isStartled();
    }

    @Override
    public void start() {
        ticks = 100 + bug.getRandom().nextInt(200);
        center = bug.position().add(bug.getRandom().nextDouble() - 0.5, 0, bug.getRandom().nextDouble() - 0.5);
        angle = bug.getRandom().nextFloat() * Mth.TWO_PI;
        direction = bug.getRandom().nextBoolean() ? 1 : -1;
    }

    @Override
    public void tick() {
        ticks--;
        angle += 0.35f * direction;
        double r = 0.9;
        bug.getMoveControl().setWantedPosition(center.x + Mth.cos(angle) * r, bug.getY(), center.z + Mth.sin(angle) * r, 1.3);
    }
}
