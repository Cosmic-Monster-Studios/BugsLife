package com.bugslife.item;

import com.bugslife.entity.BugEntity;
import com.bugslife.registry.ModItems;
import com.bugslife.registry.ModTriggers;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.AreaEffectCloud;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EquipmentSlot;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.phys.Vec3;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.event.entity.living.LivingFallEvent;
import net.neoforged.neoforge.event.entity.living.LivingIncomingDamageEvent;
import net.neoforged.neoforge.event.entity.living.LivingShieldBlockEvent;
import net.neoforged.neoforge.event.entity.living.MobEffectEvent;
import org.jetbrains.annotations.Nullable;

/**
 * Chitin armour and shield perks:
 * boots halve fall damage; the full set is bug-proof (stings, bites, sprays, stink clouds and antlion grabs from bugs
 * do nothing); the shield throws damage back at attackers, and punishes bugs hardest.
 */
public final class ChitinGear {
    private ChitinGear() {
    }

    public static boolean bugProof(@Nullable Entity entity) {
        return entity instanceof LivingEntity l
                && l.getItemBySlot(EquipmentSlot.HEAD).is(ModItems.CHITIN_HELMET.get())
                && l.getItemBySlot(EquipmentSlot.CHEST).is(ModItems.CHITIN_CHESTPLATE.get())
                && l.getItemBySlot(EquipmentSlot.LEGS).is(ModItems.CHITIN_LEGGINGS.get())
                && l.getItemBySlot(EquipmentSlot.FEET).is(ModItems.CHITIN_BOOTS.get());
    }

    private static boolean fromBug(@Nullable Entity source) {
        return source instanceof BugEntity || source instanceof AreaEffectCloud cloud && cloud.getOwner() instanceof BugEntity;
    }

    @SubscribeEvent
    public static void onFall(LivingFallEvent event) {
        if (event.getEntity().getItemBySlot(EquipmentSlot.FEET).is(ModItems.CHITIN_BOOTS.get())) {
            event.setDamageMultiplier(event.getDamageMultiplier() * 0.5f);
        }
    }

    /** Bugs cannot hurt someone in a full chitin set. */
    @SubscribeEvent
    public static void onDamage(LivingIncomingDamageEvent event) {
        if (fromBug(event.getSource().getEntity()) && bugProof(event.getEntity())) {
            event.setCanceled(true);
        }
    }

    /** Nor poison, sicken or slow them. */
    @SubscribeEvent
    public static void onEffect(MobEffectEvent.Applicable event) {
        if (fromBug(event.getEffectSource()) && bugProof(event.getEntity())) {
            event.setResult(MobEffectEvent.Applicable.Result.DO_NOT_APPLY);
        }
    }

    /** The chitin shield throws the blow back. */
    @SubscribeEvent
    public static void onBlock(LivingShieldBlockEvent event) {
        LivingEntity blocker = event.getEntity();
        if (!event.getBlocked() || !blocker.getUseItem().is(ModItems.CHITIN_SHIELD.get())) return;
        if (!(event.getDamageSource().getDirectEntity() instanceof LivingEntity attacker) || attacker.distanceToSqr(blocker) > 25) return;
        boolean bug = attacker instanceof BugEntity;
        attacker.hurt(blocker.damageSources().thorns(blocker), bug ? 4.0f : 2.0f);
        Vec3 away = attacker.position().subtract(blocker.position()).normalize();
        attacker.knockback(bug ? 1.2 : 0.6, -away.x, -away.z);
        if (blocker.level() instanceof ServerLevel level) {
            level.sendParticles(ParticleTypes.CRIT, attacker.getX(), attacker.getY(0.5), attacker.getZ(), 8, 0.2, 0.2, 0.2, 0.1);
            level.playSound(null, blocker.blockPosition(), SoundEvents.ARMOR_EQUIP_TURTLE.value(), SoundSource.PLAYERS, 0.8f, 1.6f);
        }
        if (blocker instanceof ServerPlayer sp) {
            ModTriggers.BUG_ACTION.get().trigger(sp, "shield_reflect");
        }
    }
}
