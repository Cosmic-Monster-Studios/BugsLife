package com.bugslife.entity.goal;

import com.bugslife.entity.BugEntity;
import net.minecraft.world.entity.ai.goal.PanicGoal;

/** Panics when hurt, burning, or startled by a missed net swing. */
public class BugPanicGoal extends PanicGoal {
    private final BugEntity bug;

    public BugPanicGoal(BugEntity bug, double speed) {
        super(bug, speed);
        this.bug = bug;
    }

    @Override
    protected boolean shouldPanic() {
        return super.shouldPanic() || bug.isStartled();
    }
}
