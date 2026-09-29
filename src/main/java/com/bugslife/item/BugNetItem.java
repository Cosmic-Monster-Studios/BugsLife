package com.bugslife.item;

import com.bugslife.bug.BugData;
import com.bugslife.bug.BugRarity;
import com.bugslife.bug.JournalEvents;
import com.bugslife.entity.BugEntity;
import com.bugslife.registry.ModItems;
import net.minecraft.ChatFormatting;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.ClipContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.HitResult;
import net.minecraft.world.phys.Vec3;
import org.jetbrains.annotations.Nullable;

import java.util.List;
import java.util.Optional;

/**
 * Right-click a bug to swing the net. Rarer bugs slip away more often; sneaking up (crouching), catching a bug
 * while it rests, clings to bark, is rolled up or frozen all help. A catch needs an empty Bug Jar.
 */
public class BugNetItem extends Item {
    private final boolean silk;

    public BugNetItem(boolean silk, Properties properties) {
        super(properties);
        this.silk = silk;
    }

    public float catchChance(BugEntity bug, Player player) {
        BugRarity rarity = bug.species().rarity();
        float chance = silk ? rarity.silkNetChance : rarity.netChance;
        if (player.isShiftKeyDown()) chance += 0.15f;
        if (bug.hasFlag(BugEntity.FLAG_ROLLED) || bug.hasFlag(BugEntity.FLAG_FROZEN)) chance += 0.25f;
        if (bug.isClinging() || bug.hasFlag(BugEntity.FLAG_PERCHED)) chance += 0.1f;
        if (bug.isBaby()) chance += 0.1f;
        if (bug.isStartled()) chance -= 0.2f;
        return chance;
    }

    /** How far past a bug's hitbox a swing still counts, in blocks. Bugs are tiny; this forgives a near miss. */
    public static final double AIM_ASSIST = 0.3;

    @Override
    public InteractionResult interactLivingEntity(ItemStack stack, Player player, LivingEntity target, InteractionHand hand) {
        if (!(target instanceof BugEntity bug) || !bug.isAlive()) {
            return InteractionResult.PASS;
        }
        return swingAt(stack, player, bug, hand);
    }

    /** A swing that misses every hitbox still catches the bug it passed closest to. */
    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        ItemStack stack = player.getItemInHand(hand);
        BugEntity bug = nearMiss(player);
        if (bug == null) return InteractionResultHolder.pass(stack);
        InteractionResult result = swingAt(stack, player, bug, hand);
        return new InteractionResultHolder<>(result, stack);
    }

    @Nullable
    public static BugEntity nearMiss(Player player) {
        double reach = player.entityInteractionRange() + AIM_ASSIST;
        Vec3 eye = player.getEyePosition();
        Vec3 end = eye.add(player.getViewVector(1.0f).scale(reach));
        // stop at the first solid block, so a bug behind a wall can't be netted
        HitResult block = player.level().clip(new ClipContext(eye, end, ClipContext.Block.COLLIDER, ClipContext.Fluid.NONE, player));
        double limit = block.getType() == HitResult.Type.MISS ? reach * reach : eye.distanceToSqr(block.getLocation()) + 0.25;
        BugEntity best = null;
        double bestDist = limit;
        for (BugEntity bug : player.level().getEntitiesOfClass(BugEntity.class, new AABB(eye, end).inflate(AIM_ASSIST + 1.0), BugEntity::isAlive)) {
            AABB box = bug.getBoundingBox().inflate(AIM_ASSIST);
            Optional<Vec3> hit = box.contains(eye) ? Optional.of(eye) : box.clip(eye, end);
            if (hit.isEmpty()) continue;
            double d = eye.distanceToSqr(hit.get());
            if (d < bestDist) {
                bestDist = d;
                best = bug;
            }
        }
        return best;
    }

    private InteractionResult swingAt(ItemStack stack, Player player, BugEntity bug, InteractionHand hand) {
        if (!com.bugslife.entity.SpecialBehaviors.catchable(bug)) {
            if (!player.level().isClientSide) {
                player.displayClientMessage(Component.translatable("bugslife.msg.underground").withStyle(ChatFormatting.GRAY), true);
            }
            return InteractionResult.PASS;
        }
        if (player.getCooldowns().isOnCooldown(this)) {
            return InteractionResult.PASS;
        }
        player.swing(hand);
        if (player.level().isClientSide || !(player instanceof ServerPlayer serverPlayer)) {
            return InteractionResult.SUCCESS;
        }
        ServerLevel level = serverPlayer.serverLevel();
        player.getCooldowns().addCooldown(this, 8);
        level.playSound(null, player.blockPosition(), SoundEvents.PLAYER_ATTACK_SWEEP, SoundSource.PLAYERS, 0.5f, 1.6f);

        ItemStack jar = findEmptyJar(player);
        boolean creative = player.getAbilities().instabuild;
        if (jar.isEmpty() && !creative) {
            player.displayClientMessage(Component.translatable("bugslife.msg.need_jar").withStyle(ChatFormatting.YELLOW), true);
            return InteractionResult.CONSUME;
        }

        stack.hurtAndBreak(1, player, LivingEntity.getSlotForHand(hand));
        if (player.getRandom().nextFloat() < catchChance(bug, player)) {
            BugData data = bug.toData();
            if (!creative) jar.shrink(1);
            ItemStack filled = BugJarItem.filled(data);
            if (bug.hasCustomName()) {
                filled.set(net.minecraft.core.component.DataComponents.CUSTOM_NAME, bug.getCustomName());
            }
            if (!player.getInventory().add(filled)) {
                player.drop(filled, false);
            }
            level.sendParticles(ParticleTypes.POOF, bug.getX(), bug.getY() + 0.2, bug.getZ(), 6, 0.15, 0.15, 0.15, 0.01);
            level.playSound(null, bug.blockPosition(), SoundEvents.BOTTLE_FILL, SoundSource.PLAYERS, 0.8f, 1.3f);
            JournalEvents.recordCatch(serverPlayer, data);
            bug.discard();
        } else {
            bug.startle(player);
            level.sendParticles(ParticleTypes.CLOUD, bug.getX(), bug.getY() + 0.2, bug.getZ(), 3, 0.1, 0.1, 0.1, 0.01);
            player.displayClientMessage(Component.translatable("bugslife.msg.slipped", bug.species().displayName())
                    .withStyle(ChatFormatting.GRAY), true);
        }
        return InteractionResult.CONSUME;
    }

    private static ItemStack findEmptyJar(Player player) {
        ItemStack off = player.getOffhandItem();
        if (isEmptyJar(off)) return off;
        for (ItemStack s : player.getInventory().items) {
            if (isEmptyJar(s)) return s;
        }
        return ItemStack.EMPTY;
    }

    private static boolean isEmptyJar(ItemStack s) {
        return s.is(ModItems.BUG_JAR.get()) && BugJarItem.getBug(s) == null;
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("item.bugslife.bug_net.tip").withStyle(ChatFormatting.GRAY));
        if (silk) {
            tooltip.add(Component.translatable("item.bugslife.silk_net.tip").withStyle(ChatFormatting.AQUA));
        }
    }

    @Override
    public int getEnchantmentValue() {
        return 10;
    }
}
