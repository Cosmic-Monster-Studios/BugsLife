package com.bugslife.entity.goal;

import com.bugslife.bug.BugSpecies;
import com.bugslife.entity.BugEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.ai.goal.Goal;
import org.jetbrains.annotations.Nullable;

import java.util.EnumSet;

/** Moths are drawn to bright lights after dark and spiral around them. Void moths love end rods at any hour. */
public class LightOrbitGoal extends Goal {
    private final BugEntity bug;
    private final java.util.function.Predicate<net.minecraft.world.level.block.state.BlockState> isLight;
    private BlockPos light;
    private int ticks;
    private int cooldown;
    private float angle;

    public LightOrbitGoal(BugEntity bug) {
        this(bug, null);
    }

    /** @param isLight what counts as a light; null means any block with light level 10 or more */
    public LightOrbitGoal(BugEntity bug, java.util.function.Predicate<net.minecraft.world.level.block.state.BlockState> isLight) {
        this.bug = bug;
        this.isLight = isLight;
        setFlags(EnumSet.of(Flag.MOVE));
    }

    private boolean active() {
        return isLight != null || bug.species() == BugSpecies.VOID_MOTH || !bug.level().isDay();
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
        if (!active() || bug.isStartled() || bug.getRandom().nextInt(40) != 0) return false;
        light = findLight();
        if (light == null) cooldown = 100;
        return light != null;
    }

    @Override
    public boolean canContinueToUse() {
        return light != null && ticks > 0 && active() && !bug.isStartled()
                && lit(light);
    }

    @Override
    public void start() {
        ticks = 300 + bug.getRandom().nextInt(400);
        angle = bug.getRandom().nextFloat() * Mth.TWO_PI;
    }

    @Override
    public void tick() {
        ticks--;
        if (bug.getNavigation().isDone() || bug.tickCount % 10 == 0) {
            angle += 0.7f;
            double r = 1.2 + 0.3 * Mth.sin(angle * 0.3f);
            double x = light.getX() + 0.5 + Mth.cos(angle) * r;
            double y = light.getY() + 0.6 + 0.5 * Mth.sin(angle * 0.5f);
            double z = light.getZ() + 0.5 + Mth.sin(angle) * r;
            if (bug.level().getBlockState(BlockPos.containing(x, y, z)).isAir()) {
                bug.getNavigation().moveTo(x, y, z, 1.1);
            }
        }
    }

    @Override
    public void stop() {
        light = null;
        cooldown = 200;
    }

    private boolean lit(BlockPos p) {
        var state = bug.level().getBlockState(p);
        return isLight != null ? isLight.test(state) : state.getLightEmission(bug.level(), p) >= 10;
    }

    @Nullable
    private BlockPos findLight() {
        BlockPos origin = bug.blockPosition();
        BlockPos best = null;
        double bestDist = Double.MAX_VALUE;
        for (BlockPos p : BlockPos.betweenClosed(origin.offset(-8, -4, -8), origin.offset(8, 4, 8))) {
            if (lit(p)) {
                double d = p.distSqr(origin);
                if (d < bestDist) {
                    bestDist = d;
                    best = p.immutable();
                }
            }
        }
        return best;
    }
}
