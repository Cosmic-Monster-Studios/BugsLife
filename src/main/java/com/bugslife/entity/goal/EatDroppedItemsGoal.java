package com.bugslife.entity.goal;

import com.bugslife.entity.BugEntity;
import com.bugslife.registry.ModItems;
import net.minecraft.core.particles.ItemParticleOption;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.ItemStack;

import java.util.EnumSet;
import java.util.List;
import java.util.function.Predicate;

/** Termites tidy up: they chew through dropped wooden items and leave frass behind. */
public class EatDroppedItemsGoal extends Goal {
    private final BugEntity bug;
    private final Predicate<ItemStack> food;
    private ItemEntity target;
    private int eaten;

    public EatDroppedItemsGoal(BugEntity bug, Predicate<ItemStack> food) {
        this.bug = bug;
        this.food = food;
        setFlags(EnumSet.of(Flag.MOVE));
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }

    @Override
    public boolean canUse() {
        if (bug.getRandom().nextInt(20) != 0) return false;
        List<ItemEntity> items = bug.level().getEntitiesOfClass(ItemEntity.class, bug.getBoundingBox().inflate(8),
                e -> e.isAlive() && food.test(e.getItem()));
        target = items.isEmpty() ? null : items.get(0);
        return target != null;
    }

    @Override
    public boolean canContinueToUse() {
        return target != null && target.isAlive() && !bug.isStartled();
    }

    @Override
    public void start() {
        bug.getNavigation().moveTo(target, 1.0);
    }

    @Override
    public void tick() {
        if (bug.distanceToSqr(target) < 0.8) {
            if (bug.tickCount % 30 == 0 && bug.level() instanceof ServerLevel level) {
                ItemStack stack = target.getItem();
                level.sendParticles(new ItemParticleOption(ParticleTypes.ITEM, stack.copyWithCount(1)),
                        target.getX(), target.getY() + 0.1, target.getZ(), 4, 0.05, 0.05, 0.05, 0.03);
                bug.playSound(SoundEvents.GENERIC_EAT, 0.3f, 1.8f);
                stack.shrink(1);
                target.setItem(stack);
                if (stack.isEmpty()) target.discard();
                if (++eaten % 3 == 0) {
                    bug.spawnAtLocation(new ItemStack(ModItems.FRASS.get()));
                }
            }
        } else if (bug.getNavigation().isDone()) {
            bug.getNavigation().moveTo(target, 1.0);
        }
    }

    @Override
    public void stop() {
        target = null;
    }
}
