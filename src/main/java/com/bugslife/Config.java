package com.bugslife;

import net.neoforged.neoforge.common.ModConfigSpec;

public final class Config {
    private static final ModConfigSpec.Builder BUILDER = new ModConfigSpec.Builder();

    public static final ModConfigSpec.IntValue SPAWN_INTERVAL = BUILDER
            .comment("Ticks between bug spawn passes around each player.")
            .defineInRange("spawnInterval", 60, 10, 2400);
    public static final ModConfigSpec.IntValue SPAWN_ATTEMPTS = BUILDER
            .comment("Random habitat samples per spawn pass.")
            .defineInRange("spawnAttempts", 12, 1, 64);
    public static final ModConfigSpec.IntValue MAX_BUGS_NEAR_PLAYER = BUILDER
            .comment("Wild bugs allowed within 48 blocks of a player before spawning pauses.")
            .defineInRange("maxBugsNearPlayer", 14, 0, 128);
    public static final ModConfigSpec.DoubleValue SPAWN_CHANCE_MULTIPLIER = BUILDER
            .comment("Multiplies every bug's spawn chance. Raise it to make rare bugs easier to find.")
            .defineInRange("spawnChanceMultiplier", 1.0, 0.0, 20.0);
    public static final ModConfigSpec.DoubleValue TERRARIUM_SPEED = BUILDER
            .comment("Multiplies how fast bugs in terrariums produce harvests.")
            .defineInRange("terrariumSpeed", 1.0, 0.05, 20.0);

    public static final ModConfigSpec.BooleanValue ORB_WEAVERS_SPIN_WEBS = BUILDER
            .comment("Orb weaver spiders spin real cobwebs near trees and fences at night (at most 2 per area).")
            .define("orbWeaversSpinWebs", true);

    public static final ModConfigSpec SPEC = BUILDER.build();

    private Config() {
    }
}
