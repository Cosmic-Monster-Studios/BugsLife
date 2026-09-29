package com.bugslife.spawn;

import com.bugslife.Config;
import com.bugslife.bug.BugSpecies;
import com.bugslife.entity.BugEntity;
import com.bugslife.registry.ModEntities;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.Mth;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.level.GameRules;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.AABB;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.event.tick.LevelTickEvent;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Predicate;

/**
 * Spawns bugs in their habitats around each player. Vanilla biome spawning cannot express "on birch bark" or
 * "hanging from a lush cave ceiling", so every few seconds this samples random spots near each player, asks every
 * species whether the spot suits it, and picks one weighted by rarity.
 */
public final class BugSpawner {
    private static final double CHECK_RADIUS = 48;

    private BugSpawner() {
    }

    @SubscribeEvent
    public static void onLevelTick(LevelTickEvent.Post event) {
        if (!(event.getLevel() instanceof ServerLevel level)) return;
        if (!level.getGameRules().getBoolean(GameRules.RULE_DOMOBSPAWNING)) return;
        if (level.getGameTime() % Config.SPAWN_INTERVAL.get() != 0) return;
        for (ServerPlayer player : level.players()) {
            if (!player.isSpectator()) {
                spawnAround(level, player);
            }
        }
    }

    private record Candidate(BugSpecies species, BlockPos pos) {
    }

    private static void spawnAround(ServerLevel level, ServerPlayer player) {
        RandomSource random = level.getRandom();
        AABB area = player.getBoundingBox().inflate(CHECK_RADIUS);
        int wild = level.getEntitiesOfClass(BugEntity.class, area, b -> !b.isFromJar()).size();
        if (wild >= Config.MAX_BUGS_NEAR_PLAYER.get()) return;

        boolean day = level.isDay();
        List<Candidate> candidates = new ArrayList<>();
        int attempts = Config.SPAWN_ATTEMPTS.get();
        for (int i = 0; i < attempts; i++) {
            float angle = random.nextFloat() * Mth.TWO_PI;
            double dist = 10 + random.nextDouble() * 30;
            BlockPos origin = BlockPos.containing(player.getX() + Mth.cos(angle) * dist,
                    player.getY() + random.nextInt(33) - 16, player.getZ() + Mth.sin(angle) * dist);
            if (!level.isLoaded(origin) || origin.getY() < level.getMinBuildHeight() || origin.getY() >= level.getMaxBuildHeight()) {
                continue;
            }
            for (BugSpecies species : BugSpecies.values()) {
                switch (species.spawnTime()) {
                    case DAY -> {
                        if (!day) continue;
                    }
                    case NIGHT -> {
                        if (day) continue;
                    }
                    default -> {
                    }
                }
                BlockPos pos = species.habitat().find(level, origin, random);
                if (pos != null) {
                    candidates.add(new Candidate(species, pos));
                }
            }
        }
        if (candidates.isEmpty()) return;

        int total = 0;
        for (Candidate c : candidates) total += c.species().rarity().weight;
        int roll = random.nextInt(total);
        Candidate chosen = candidates.get(0);
        for (Candidate c : candidates) {
            roll -= c.species().rarity().weight;
            if (roll < 0) {
                chosen = c;
                break;
            }
        }
        final Candidate pick = chosen;
        double chance = pick.species().rarity().spawnChance * Config.SPAWN_CHANCE_MULTIPLIER.get();
        if (random.nextDouble() >= chance) return;

        int sameNearby = level.getEntitiesOfClass(BugEntity.class, new AABB(pick.pos()).inflate(24),
                b -> b.species() == pick.species()).size();
        if (sameNearby >= 6) return;
        int count = Mth.nextInt(random, pick.species().groupMin(), pick.species().groupMax());
        for (int n = 0; n < count; n++) {
            BlockPos pos = n == 0 ? pick.pos() : jitter(level, pick, random);
            if (pos != null) {
                spawn(level, pick.species(), pos, random);
            }
        }
    }

    private static BlockPos jitter(ServerLevel level, Candidate pick, RandomSource random) {
        for (int i = 0; i < 4; i++) {
            BlockPos p = pick.pos().offset(random.nextInt(5) - 2, random.nextInt(3) - 1, random.nextInt(5) - 2);
            BlockPos found = pick.species().habitat().find(level, p, random);
            if (found != null) return found;
        }
        return null;
    }

    public static BugEntity spawn(ServerLevel level, BugSpecies species, BlockPos pos, RandomSource random) {
        BugEntity bug = ModEntities.get(species).get().create(level);
        if (bug == null) return null;
        bug.moveTo(pos.getX() + 0.5, pos.getY(), pos.getZ() + 0.5, random.nextFloat() * 360f, 0);
        if (!level.noCollision(bug)) return null;
        bug.finalizeSpawn(level, level.getCurrentDifficultyAt(pos), MobSpawnType.NATURAL, null);
        Predicate<BlockState> bark = BugEntity.barkFor(species);
        if (bark != null) {
            for (Direction d : Direction.Plane.HORIZONTAL) {
                if (bark.test(level.getBlockState(pos.relative(d)))) {
                    bug.startCling(d, 0, 600 + random.nextInt(1200));
                    break;
                }
            }
        }
        level.addFreshEntity(bug);
        return bug;
    }
}
