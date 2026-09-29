package com.bugslife.entity.goal;

import com.bugslife.entity.BugEntity;
import com.bugslife.registry.ModTriggers;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.player.Player;

import java.util.EnumSet;

/** At night a hungry mosquito homes in on the nearest player, bites once, and flies off full. */
public class MosquitoBiteGoal extends Goal {
    private final BugEntity bug;
    private Player target;
    private int ticks;

    public MosquitoBiteGoal(BugEntity bug) {
        this.bug = bug;
        setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
    }

    @Override
    public boolean requiresUpdateEveryTick() {
        return true;
    }

    @Override
    public boolean canUse() {
        if (bug.hasFlag(BugEntity.FLAG_ALERT) || bug.level().isDay() || bug.isFromJar() || bug.getRandom().nextInt(20) != 0) return false;
        Player p = bug.level().getNearestPlayer(bug, 12);
        if (p == null || p.isCreative() || p.isSpectator() || p.isInWater() || com.bugslife.item.ChitinGear.bugProof(p)) return false;
        target = p;
        return true;
    }

    @Override
    public boolean canContinueToUse() {
        return target != null && target.isAlive() && ticks > 0 && !bug.hasFlag(BugEntity.FLAG_ALERT) && !bug.isStartled();
    }

    @Override
    public void start() {
        ticks = 400;
        playWhine();
    }

    private void playWhine() {
        bug.playSound(SoundEvents.BEE_LOOP, 0.5f, 2.0f);
    }

    @Override
    public void tick() {
        ticks--;
        if (bug.tickCount % 40 == 0) playWhine();
        if (bug.tickCount % 5 == 0) {
            bug.getNavigation().moveTo(target.getX(), target.getEyeY() - 0.4, target.getZ(), 1.3);
        }
        if (bug.distanceToSqr(target.getX(), target.getEyeY() - 0.4, target.getZ()) < 1.2) {
            target.hurt(bug.damageSources().mobAttack(bug), 1.0f);
            target.addEffect(new MobEffectInstance(MobEffects.HUNGER, 100, 0), bug);
            bug.setFlag(BugEntity.FLAG_ALERT, true);
            bug.specialTimer = 2400;
            if (target instanceof ServerPlayer sp) {
                ModTriggers.BUG_ACTION.get().trigger(sp, "bitten");
            }
            ticks = 0;
        }
    }

    @Override
    public void stop() {
        target = null;
    }
}
