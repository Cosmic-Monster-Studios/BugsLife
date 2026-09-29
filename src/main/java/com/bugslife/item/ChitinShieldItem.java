package com.bugslife.item;

import com.bugslife.registry.ModItems;
import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.ShieldItem;
import net.minecraft.world.item.TooltipFlag;

import java.util.List;

/** A beetle-shell shield: blocks like any shield and throws damage back at whoever struck it (see ChitinGear). */
public class ChitinShieldItem extends ShieldItem {
    public ChitinShieldItem(Properties properties) {
        super(properties);
    }

    @Override
    public boolean isValidRepairItem(ItemStack stack, ItemStack repair) {
        return repair.is(ModItems.CHITIN.get()) || super.isValidRepairItem(stack, repair);
    }

    @Override
    public void appendHoverText(ItemStack stack, TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("item.bugslife.chitin_shield.tip").withStyle(ChatFormatting.GRAY));
    }
}
