package com.bugslife.bug;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.util.StringRepresentable;

public enum BugRarity implements StringRepresentable {
    //          color                      weight  spawn  net    silk   produce ticks
    COMMON(ChatFormatting.WHITE, 100, 1.00f, 1.00f, 1.00f, 2400),
    UNCOMMON(ChatFormatting.GREEN, 45, 0.70f, 0.80f, 1.00f, 3600),
    RARE(ChatFormatting.AQUA, 15, 0.40f, 0.55f, 0.85f, 4800),
    EPIC(ChatFormatting.LIGHT_PURPLE, 5, 0.20f, 0.30f, 0.65f, 7200),
    LEGENDARY(ChatFormatting.GOLD, 2, 0.10f, 0.15f, 0.40f, 9600);

    public final ChatFormatting color;
    public final int weight;
    public final float spawnChance;
    public final float netChance;
    public final float silkNetChance;
    public final int produceTicks;

    BugRarity(ChatFormatting color, int weight, float spawnChance, float netChance, float silkNetChance, int produceTicks) {
        this.color = color;
        this.weight = weight;
        this.spawnChance = spawnChance;
        this.netChance = netChance;
        this.silkNetChance = silkNetChance;
        this.produceTicks = produceTicks;
    }

    public Component displayName() {
        return Component.translatable("bugslife.rarity." + getSerializedName()).withStyle(color);
    }

    public boolean atLeast(BugRarity other) {
        return ordinal() >= other.ordinal();
    }

    @Override
    public String getSerializedName() {
        return name().toLowerCase(java.util.Locale.ROOT);
    }
}
