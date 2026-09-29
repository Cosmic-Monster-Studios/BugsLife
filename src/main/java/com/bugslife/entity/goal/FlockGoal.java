package com.bugslife.entity.goal;

import com.bugslife.entity.BugEntity;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.ai.goal.Goal;

import java.util.EnumSet;
import java.util.List;

/**
 * Locust swarms: every locust keeps station on the swarm's leader (the one with the lowest id nearby) at its own
 * offset, so the whole cloud drifts together wherever the leader wanders.
 */
public class FlockGoal extends Goal {
    private final BugEntity bug;
    private BugEntity leader;

    public FlockGoal(BugEntity bug) {
        this.bug = bug;
        setFlags(EnumSet.of(Flag.MOVE));
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }

    @Override
    public boolean canUse() {
        if (bug.hasFlag(BugEntity.FLAG_PERCHED) || bug.getRandom().nextInt(10) != 0) return false;
        List<BugEntity> flock = bug.level().getEntitiesOfClass(BugEntity.class, bug.getBoundingBox().inflate(20),
                b -> b.species() == bug.species() && b.getId() < bug.getId());
        leader = null;
        for (BugEntity b : flock) {
            if (leader == null || b.getId() < leader.getId()) leader = b;
        }
        return leader != null;
    }

    @Override
    public boolean canContinueToUse() {
        return leader != null && leader.isAlive() && !bug.hasFlag(BugEntity.FLAG_PERCHED);
    }

    @Override
    public void tick() {
        if (bug.tickCount % 8 != 0) return;
        float angle = (bug.getId() * 2.399963f) % Mth.TWO_PI;
        double r = 1.0 + (bug.getId() % 4) * 0.6;
        double x = leader.getX() + Mth.cos(angle + bug.tickCount * 0.01f) * r;
        double y = leader.getY() + ((bug.getId() % 5) - 2) * 0.4;
        double z = leader.getZ() + Mth.sin(angle + bug.tickCount * 0.01f) * r;
        bug.getNavigation().moveTo(x, y, z, 1.4);
    }

    @Override
    public void stop() {
        leader = null;
    }
}
