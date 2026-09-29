package com.bugslife.item;

import com.bugslife.bug.BugData;
import com.bugslife.bug.BugSpecies;
import com.bugslife.bug.Movement;
import com.bugslife.entity.BugEntity;
import com.bugslife.registry.ModComponents;
import com.bugslife.registry.ModItems;
import com.bugslife.registry.ModTriggers;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.component.DataComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.ItemUtils;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;
import org.jetbrains.annotations.Nullable;

import java.util.List;

/** An empty jar, or (with the {@code bugslife:bug} component) a jar holding one live bug. */
public class BugJarItem extends Item {
    public BugJarItem(Properties properties) {
        super(properties);
    }

    public static ItemStack filled(BugData data) {
        ItemStack stack = new ItemStack(ModItems.BUG_JAR.get());
        stack.set(ModComponents.BUG.get(), data);
        stack.set(DataComponents.MAX_STACK_SIZE, 1);
        return stack;
    }

    @Nullable
    public static BugData getBug(ItemStack stack) {
        return stack.get(ModComponents.BUG.get());
    }

    @Override
    public Component getName(ItemStack stack) {
        BugData data = getBug(stack);
        if (data == null) return super.getName(stack);
        return Component.translatable("item.bugslife.bug_jar.filled", data.species().displayName());
    }

    @Override
    public boolean isFoil(ItemStack stack) {
        BugData data = getBug(stack);
        return data != null && data.prismatic();
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        BugData data = getBug(stack);
        if (data == null) {
            tooltip.add(Component.translatable("item.bugslife.bug_jar.empty_tip").withStyle(ChatFormatting.GRAY));
            return;
        }
        BugSpecies s = data.species();
        tooltip.add(s.rarity().displayName());
        if (data.prismatic()) {
            tooltip.add(Component.translatable("bugslife.prismatic").withStyle(ChatFormatting.LIGHT_PURPLE, ChatFormatting.ITALIC));
        }
        if (data.baby()) {
            tooltip.add(Component.translatable("bugslife.baby").withStyle(ChatFormatting.GRAY));
        }
        tooltip.add(Component.translatable(s.descriptionKey("habitat")).withStyle(ChatFormatting.DARK_GREEN));
        tooltip.add(Component.translatable("item.bugslife.bug_jar.filled_tip").withStyle(ChatFormatting.GRAY));
    }

    /** Right-click a block with a full jar to let the bug go. (Terrariums take the bug instead.) */
    @Override
    public InteractionResult useOn(UseOnContext context) {
        ItemStack stack = context.getItemInHand();
        BugData data = getBug(stack);
        if (data == null) return InteractionResult.PASS;
        Level level = context.getLevel();
        if (!(level instanceof ServerLevel server)) return InteractionResult.SUCCESS;
        BlockPos pos = context.getClickedPos().relative(context.getClickedFace());
        BugEntity bug = BugEntity.fromData(server, data);
        if (bug == null) return InteractionResult.FAIL;
        bug.moveTo(pos.getX() + 0.5, pos.getY(), pos.getZ() + 0.5, context.getRotation() + 180f, 0);
        bug.finalizeSpawn(server, server.getCurrentDifficultyAt(pos), MobSpawnType.BUCKET, null);
        bug.setPrismatic(data.prismatic());
        if (stack.has(DataComponents.CUSTOM_NAME)) {
            bug.setCustomName(stack.get(DataComponents.CUSTOM_NAME));
        }
        if (data.species().movement() == Movement.HANG) {
            bug.attachToCeiling();
        }
        server.addFreshEntity(bug);
        server.playSound(null, pos, SoundEvents.BOTTLE_EMPTY, SoundSource.PLAYERS, 0.8f, 1.3f);
        Player player = context.getPlayer();
        if (player != null) {
            ItemStack empty = new ItemStack(ModItems.BUG_JAR.get());
            player.setItemInHand(context.getHand(), ItemUtils.createFilledResult(stack, player, empty));
            if (player instanceof ServerPlayer sp) {
                ModTriggers.BUG_ACTION.get().trigger(sp, "release");
            }
        }
        return InteractionResult.CONSUME;
    }
}
