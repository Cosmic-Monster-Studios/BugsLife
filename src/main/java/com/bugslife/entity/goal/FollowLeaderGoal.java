package com.bugslife.entity.goal;

import com.bugslife.bug.BugSpecies;
import com.bugslife.entity.BugEntity;
import net.minecraft.world.entity.ai.goal.Goal;
import org.jetbrains.annotations.Nullable;

import java.util.EnumSet;
import java.util.List;

/**
 * Worker ants march in columns: each follows the ant ahead of it (or the queen), and the column's leader
 * wanders - often off to tend a nearby aphid.
 */
public class FollowLeaderGoal extends Goal {
    private final BugEntity ant;
    private BugEntity leader;
    private int recheck;

    public FollowLeaderGoal(BugEntity ant) {
        this.ant = ant;
        setFlags(EnumSet.of(Flag.MOVE));
    }

    @Nullable
    private BugEntity findLeader() {
        List<BugEntity> near = ant.level().getEntitiesOfClass(BugEntity.class, ant.getBoundingBox().inflate(12),
                b -> b != ant && (b.species() == BugSpecies.QUEEN_ANT || b.species() == BugSpecies.WORKER_ANT));
        BugEntity best = null;
        double bestDist = Double.MAX_VALUE;
        for (BugEntity b : near) {
            if (b.species() == BugSpecies.QUEEN_ANT) {
                return b;
            }
            // follow an ant with a lower id: that makes chains, never loops
            if (b.getId() < ant.getId()) {
                double d = b.distanceToSqr(ant);
                if (d < bestDist) {
                    bestDist = d;
                    best = b;
                }
            }
        }
        return best;
    }

    @Override
    public boolean canUse() {
        if (ant.isStartled() || ant.getRandom().nextInt(10) != 0) return false;
        leader = findLeader();
        return leader != null && leader.distanceToSqr(ant) > 2.0;
    }

    @Override
    public boolean canContinueToUse() {
        return leader != null && leader.isAlive() && !ant.isStartled() && leader.distanceToSqr(ant) > 1.2;
    }

    @Override
    public void start() {
        recheck = 0;
    }

    @Override
    public void tick() {
        if (--recheck <= 0) {
            recheck = 8;
            ant.getNavigation().moveTo(leader, 1.1);
        }
    }

    @Override
    public void stop() {
        leader = null;
        ant.getNavigation().stop();
    }
}
