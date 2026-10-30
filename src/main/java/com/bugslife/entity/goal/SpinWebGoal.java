package com.bugslife.entity.goal;

import com.bugslife.Config;
import com.bugslife.entity.BugEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import org.jetbrains.annotations.Nullable;

import java.util.EnumSet;

/**
 * Orb weavers spin a real cobweb at dusk between a trunk or fence and open air, a couple of blocks up, and keep
 * at most a few webs nearby. Flying bugs that blunder in get stuck, and the spider comes to eat them.
 */
public class SpinWebGoal extends Goal {
    private final BugEntity spider;
    private BlockPos spot;
    private int ticks;

    public SpinWebGoal(BugEntity spider) {
        this.spider = spider;
        setFlags(EnumSet.of(Flag.MOVE));
    }

    @Override
    public boolean canUse() {
        if (spider.specialCooldown > 0 || !canSpin()) return false;
        if (spider.level().isDay() || spider.getRandom().nextInt(200) != 0) return false;
        if (countWebs() >= 2) {
            spider.specialCooldown = 2400;
            return false;
        }
        spot = findSpot();
        return spot != null;
    }

    private boolean canSpin() {
        return Config.ORB_WEAVERS_SPIN_WEBS.get() && !spider.isFromJar()
                && com.bugslife.entity.SpecialBehaviors.canGrief(spider);
    }

    private int countWebs() {
        int n = 0;
        BlockPos o = spider.blockPosition();
        for (BlockPos p : BlockPos.betweenClosed(o.offset(-8, -4, -8), o.offset(8, 4, 8))) {
            if (spider.level().getBlockState(p).is(Blocks.COBWEB)) n++;
        }
        return n;
    }

    @Nullable
    private BlockPos findSpot() {
        Level level = spider.level();
        for (int i = 0; i < 30; i++) {
            BlockPos p = spider.blockPosition().offset(spider.getRandom().nextInt(9) - 4, spider.getRandom().nextInt(4), spider.getRandom().nextInt(9) - 4);
            // open air below the web too, so flying bugs can blunder into it
            if (!level.getBlockState(p).isAir() || !level.getBlockState(p.below()).isAir()) continue;
            for (Direction d : Direction.Plane.HORIZONTAL) {
                BlockState side = level.getBlockState(p.relative(d));
                if (side.is(BlockTags.LOGS) || side.is(BlockTags.FENCES) || side.is(BlockTags.LEAVES)) {
                    return p.immutable();
                }
            }
        }
        return null;
    }

    @Override
    public boolean canContinueToUse() {
        return spot != null && ticks > 0 && canSpin();
    }

    @Override
    public void start() {
        ticks = 300;
        spider.getNavigation().moveTo(spot.getX() + 0.5, spot.getY(), spot.getZ() + 0.5, 1.0);
    }

    @Override
    public void tick() {
        if (spot == null || !canSpin()) {
            ticks = 0;
            spider.getNavigation().stop();
            return;
        }
        ticks--;
        if (spider.distanceToSqr(spot.getX() + 0.5, spot.getY() + 0.5, spot.getZ() + 0.5) < 4.0
                && spider.level().getBlockState(spot).isAir()) {
            // Another weaver may have placed a web since this goal acquired its spot.
            if (countWebs() >= 2) {
                spider.specialCooldown = 2400;
                ticks = 0;
                spider.getNavigation().stop();
                return;
            }
            spider.level().setBlockAndUpdate(spot, Blocks.COBWEB.defaultBlockState());
            spider.playSound(SoundEvents.SPIDER_AMBIENT, 0.3f, 2.0f);
            spider.specialCooldown = 6000;
            ticks = 0;
        } else if (spider.getNavigation().isDone()) {
            spider.getNavigation().moveTo(spot.getX() + 0.5, spot.getY(), spot.getZ() + 0.5, 1.0);
        }
    }

    @Override
    public void stop() {
        spot = null;
    }
}
