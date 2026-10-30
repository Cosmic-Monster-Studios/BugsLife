package com.bugslife.bug;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.BiomeTags;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.animal.Cow;
import net.minecraft.world.entity.animal.Pig;
import net.minecraft.world.entity.animal.Sheep;
import net.minecraft.world.entity.animal.goat.Goat;
import net.minecraft.world.entity.animal.horse.AbstractHorse;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LightLayer;
import net.minecraft.world.level.biome.Biomes;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.AABB;
import org.jetbrains.annotations.Nullable;

import java.util.Set;
import java.util.function.Predicate;

/**
 * Habitat rules for every bug. Each takes a random point near a player and either returns the exact
 * position to spawn in or null. Day/night is checked by the spawner from {@link BugSpecies#spawnTime()}.
 */
public final class Habitats {
    private Habitats() {
    }

    // ------------------------------------------------------------------ helpers

    static boolean overworld(ServerLevel level) {
        return level.dimension() == Level.OVERWORLD;
    }

    /** First air block above the ground at this column (ignores leaves), or null if that is water. */
    @Nullable
    static BlockPos surface(ServerLevel level, BlockPos origin) {
        int y = level.getHeight(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, origin.getX(), origin.getZ());
        BlockPos pos = new BlockPos(origin.getX(), y, origin.getZ());
        if (!level.getFluidState(pos.below()).isEmpty()) {
            return null;
        }
        return pos;
    }

    /** Drops from origin to the first air block that sits on a solid floor, within maxDown blocks. */
    @Nullable
    static BlockPos floor(ServerLevel level, BlockPos origin, int maxDown) {
        return floor(level, origin, maxDown, s -> false);
    }

    /** As {@link #floor(ServerLevel, BlockPos, int)}, but a thin cover block (carpet, vein) accepted by cover may sit on the floor. */
    @Nullable
    static BlockPos floor(ServerLevel level, BlockPos origin, int maxDown, Predicate<BlockState> cover) {
        BlockPos.MutableBlockPos pos = origin.mutable();
        if (!level.getBlockState(pos).isAir()) {
            return null;
        }
        for (int i = 0; i < maxDown; i++) {
            BlockState below = level.getBlockState(pos.below());
            if (!below.isAir()) {
                if (cover.test(below)) {
                    BlockPos under = pos.below(2);
                    return level.getBlockState(under).isFaceSturdy(level, under, Direction.UP) ? pos.immutable() : null;
                }
                return below.isFaceSturdy(level, pos.below(), Direction.UP) ? pos.immutable() : null;
            }
            pos.move(Direction.DOWN);
        }
        return null;
    }

    /** Rises from origin to the air block directly under a solid ceiling, within maxUp blocks. */
    @Nullable
    static BlockPos ceiling(ServerLevel level, BlockPos origin, int maxUp) {
        BlockPos.MutableBlockPos pos = origin.mutable();
        if (!level.getBlockState(pos).isAir()) {
            return null;
        }
        for (int i = 0; i < maxUp; i++) {
            BlockState above = level.getBlockState(pos.above());
            if (!above.isAir()) {
                return above.isFaceSturdy(level, pos.above(), Direction.DOWN) ? pos.immutable() : null;
            }
            pos.move(Direction.UP);
        }
        return null;
    }

    static boolean nearBlock(ServerLevel level, BlockPos center, int r, int ry, Predicate<BlockState> test) {
        for (BlockPos p : BlockPos.betweenClosed(center.offset(-r, -ry, -r), center.offset(r, ry, r))) {
            if (test.test(level.getBlockState(p))) {
                return true;
            }
        }
        return false;
    }

    /** An air block horizontally next to a block matching test (the bug clings to that block's side). */
    @Nullable
    static BlockPos besideBlock(ServerLevel level, BlockPos origin, Predicate<BlockState> test) {
        for (BlockPos p : BlockPos.betweenClosed(origin.offset(-1, -1, -1), origin.offset(1, 1, 1))) {
            if (!level.getBlockState(p).isAir()) {
                continue;
            }
            for (Direction d : Direction.Plane.HORIZONTAL) {
                if (test.test(level.getBlockState(p.relative(d)))) {
                    return p.immutable();
                }
            }
        }
        return null;
    }

    static boolean dark(ServerLevel level, BlockPos pos, int maxBlockLight) {
        return level.getBrightness(LightLayer.BLOCK, pos) <= maxBlockLight && !level.canSeeSky(pos);
    }

    static final Set<Block> PILL_BUG_FLOORS = Set.of(Blocks.MOSS_BLOCK, Blocks.MOSSY_COBBLESTONE, Blocks.PODZOL,
            Blocks.COARSE_DIRT, Blocks.ROOTED_DIRT, Blocks.MUD, Blocks.MUDDY_MANGROVE_ROOTS, Blocks.MOSSY_STONE_BRICKS);
    static final Set<Block> CAVE_FLOORS = Set.of(Blocks.STONE, Blocks.DEEPSLATE, Blocks.TUFF, Blocks.DRIPSTONE_BLOCK,
            Blocks.GRAVEL, Blocks.ANDESITE, Blocks.DIORITE, Blocks.GRANITE, Blocks.CALCITE, Blocks.COBBLESTONE, Blocks.DIRT);
    static final Set<Block> NETHER_FLOORS = Set.of(Blocks.NETHERRACK, Blocks.BASALT, Blocks.BLACKSTONE,
            Blocks.MAGMA_BLOCK, Blocks.CRIMSON_NYLIUM, Blocks.WARPED_NYLIUM, Blocks.SOUL_SOIL, Blocks.SMOOTH_BASALT);

    // ------------------------------------------------------------------ common

    /** On crops and farmland in the daytime. */
    public static BlockPos ladybug(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        BlockPos pos = surface(level, origin);
        if (pos == null) return null;
        BlockState here = level.getBlockState(pos);
        if (here.is(BlockTags.CROPS) || level.getBlockState(pos.below()).is(Blocks.FARMLAND)) return pos;
        // the odd ladybug in a flower garden
        if (here.is(BlockTags.SMALL_FLOWERS) && random.nextInt(4) == 0) return pos;
        return null;
    }

    /** Sucking sap on crops, or on top of leaves. */
    public static BlockPos aphid(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        BlockPos pos = surface(level, origin);
        if (pos != null && level.getBlockState(pos).is(BlockTags.CROPS)) return pos;
        int top = level.getHeight(Heightmap.Types.MOTION_BLOCKING, origin.getX(), origin.getZ());
        BlockPos leafTop = new BlockPos(origin.getX(), top, origin.getZ());
        if (level.getBlockState(leafTop.below()).is(BlockTags.LEAVES) && level.getBlockState(leafTop).isAir() && random.nextInt(12) == 0) {
            return leafTop;
        }
        return null;
    }

    /** Hovering over grass on warm nights, especially near water. */
    public static BlockPos firefly(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        BlockPos pos = surface(level, origin);
        if (pos == null || !level.getBlockState(pos.below()).is(Blocks.GRASS_BLOCK)) return null;
        var biome = level.getBiome(pos);
        if (biome.is(BiomeTags.IS_OCEAN) || biome.value().coldEnoughToSnow(pos) || !biome.value().hasPrecipitation()) return null;
        boolean water = nearBlock(level, pos, 5, 2, s -> s.getFluidState().is(FluidTags.WATER));
        if (!water && random.nextInt(3) != 0) return null;
        BlockPos air = pos.above(1 + random.nextInt(2));
        return level.getBlockState(air).isAir() ? air : pos;
    }

    /** Chirping around villages at night, and in plains grass. */
    public static BlockPos cricket(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        BlockPos pos = surface(level, origin);
        if (pos == null) return null;
        BlockState below = level.getBlockState(pos.below());
        boolean ground = below.is(BlockTags.DIRT) || below.is(Blocks.DIRT_PATH) || below.is(Blocks.HAY_BLOCK) || below.is(Blocks.FARMLAND);
        if (!ground) return null;
        if (level.isVillage(pos)) return pos;
        return level.getBiome(pos).is(Biomes.PLAINS) && random.nextInt(5) == 0 ? pos : null;
    }

    /** Damp, dim places: moss, podzol, mud, and the shallow caves. */
    public static BlockPos pillBug(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        BlockPos pos = floor(level, origin, 12, s -> s.is(Blocks.MOSS_CARPET));
        if (pos == null) return null;
        Block floor = level.getBlockState(pos.below()).getBlock();
        if (PILL_BUG_FLOORS.contains(floor)) return pos;
        if (level.getBlockState(pos.below()).is(Blocks.MOSS_CARPET)) return pos;
        // shaded forest floor, under the canopy
        if (level.getBlockState(pos.below()).is(BlockTags.DIRT) && !level.canSeeSky(pos) && pos.getY() > 50 && random.nextInt(3) == 0) return pos;
        if (pos.getY() > 20 && CAVE_FLOORS.contains(floor) && dark(level, pos, 7) && random.nextInt(3) == 0) return pos;
        return null;
    }

    /** Skating on still fresh water in the daytime. */
    public static BlockPos waterStrider(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        int y = level.getHeight(Heightmap.Types.WORLD_SURFACE, origin.getX(), origin.getZ());
        BlockPos water = new BlockPos(origin.getX(), y - 1, origin.getZ());
        if (!level.getFluidState(water).is(FluidTags.WATER) || !level.getFluidState(water).isSource()) return null;
        if (!level.getBlockState(water.above()).isAir()) return null;
        var biome = level.getBiome(water);
        if (biome.is(BiomeTags.IS_OCEAN) || biome.is(BiomeTags.IS_DEEP_OCEAN) || biome.value().coldEnoughToSnow(water)) return null;
        return water.above();
    }

    // ------------------------------------------------------------------ uncommon

    /** Flitting around flowers on sunny days. */
    public static BlockPos monarch(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        BlockPos pos = surface(level, origin);
        if (pos == null) return null;
        if (!nearBlock(level, pos, 2, 1, s -> s.is(BlockTags.FLOWERS))) return null;
        BlockPos air = pos.above(1 + random.nextInt(2));
        return level.getBlockState(air).isAir() ? air : null;
    }

    /** Dusk and night among birch and dark oak leaves (its caterpillars love them). */
    public static BlockPos silkMoth(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        return besideBlock(level, origin, s -> s.is(Blocks.BIRCH_LEAVES) || s.is(Blocks.DARK_OAK_LEAVES));
    }

    /** Patrolling the air over rivers, lakes and swamps. */
    public static BlockPos dragonfly(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        int y = level.getHeight(Heightmap.Types.WORLD_SURFACE, origin.getX(), origin.getZ());
        BlockPos top = new BlockPos(origin.getX(), y, origin.getZ());
        var biome = level.getBiome(top);
        if (biome.is(BiomeTags.IS_OCEAN) || biome.is(BiomeTags.IS_DEEP_OCEAN) || biome.value().coldEnoughToSnow(top)) return null;
        if (!nearBlock(level, top.below(), 3, 1, s -> s.getFluidState().is(FluidTags.WATER))) return null;
        BlockPos air = top.above(1 + random.nextInt(3));
        return level.getBlockState(air).isAir() ? air : null;
    }

    /** Wherever cows, sheep, pigs, goats and horses graze. */
    public static BlockPos dungBeetle(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        BlockPos pos = surface(level, origin);
        if (pos == null || !level.getBlockState(pos.below()).is(BlockTags.DIRT)) return null;
        var livestock = level.getEntitiesOfClass(LivingEntity.class, new AABB(pos).inflate(14),
                e -> e instanceof Cow || e instanceof Sheep || e instanceof Pig || e instanceof Goat || e instanceof AbstractHorse);
        return livestock.isEmpty() ? null : pos;
    }

    /** Pitch-dark stone caves, deep underground. */
    public static BlockPos caveWeta(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level) || origin.getY() > 50) return null;
        BlockPos pos = floor(level, origin, 10);
        if (pos == null || !dark(level, pos, 2)) return null;
        return CAVE_FLOORS.contains(level.getBlockState(pos.below()).getBlock()) ? pos : null;
    }

    // ------------------------------------------------------------------ rare

    /** Hidden in the canopy of any tree. */
    public static BlockPos walkingStick(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        BlockPos pos = besideBlock(level, origin, s -> s.is(BlockTags.LEAVES));
        return pos != null && level.canSeeSky(pos) && random.nextInt(3) == 0 ? pos : null;
    }

    /** Only on birch trunks, glittering in the sun. */
    public static BlockPos jewelBeetle(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        return besideBlock(level, origin, s -> s.is(Blocks.BIRCH_LOG));
    }

    /** On oak and dark oak trunks after dark. */
    public static BlockPos stagBeetle(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        return besideBlock(level, origin, s -> s.is(Blocks.OAK_LOG) || s.is(Blocks.DARK_OAK_LOG));
    }

    /** Hanging from cave ceilings; most common in lush and dripstone caves. */
    public static BlockPos glowworm(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level) || origin.getY() > 60) return null;
        BlockPos pos = ceiling(level, origin, 8);
        if (pos == null || !dark(level, pos, 4) || !level.getBlockState(pos.below()).isAir()) return null;
        var biome = level.getBiome(pos);
        boolean lush = biome.is(Biomes.LUSH_CAVES) || biome.is(Biomes.DRIPSTONE_CAVES);
        return lush || random.nextInt(4) == 0 ? pos.below() : null;
    }

    // ------------------------------------------------------------------ epic

    /** On jungle trunks at night, and only in the jungle. */
    public static BlockPos herculesBeetle(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level) || !level.getBiome(origin).is(BiomeTags.IS_JUNGLE)) return null;
        return besideBlock(level, origin, s -> s.is(Blocks.JUNGLE_LOG));
    }

    /** Scuttling over netherrack, basalt and nylium in the Nether. */
    public static BlockPos emberBeetle(ServerLevel level, BlockPos origin, RandomSource random) {
        if (level.dimension() != Level.NETHER) return null;
        BlockPos pos = floor(level, origin, 12);
        if (pos == null) return null;
        return NETHER_FLOORS.contains(level.getBlockState(pos.below()).getBlock()) ? pos : null;
    }

    /** Creeping over sculk in the Deep Dark. Sneak, or it will sense you. */
    public static BlockPos sculkMite(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level) || origin.getY() > 0) return null;
        BlockPos pos = floor(level, origin, 10, s -> s.is(Blocks.SCULK_VEIN));
        if (pos == null) return null;
        BlockState below = level.getBlockState(pos.below());
        return below.is(Blocks.SCULK) || below.is(Blocks.SCULK_CATALYST) || below.is(Blocks.SCULK_VEIN) ? pos : null;
    }

    // ------------------------------------------------------------------ legendary

    /** On desert sand under the stars. */
    public static BlockPos goldenScarab(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        BlockPos pos = surface(level, origin);
        if (pos == null || !level.getBiome(pos).is(Biomes.DESERT)) return null;
        return level.getBlockState(pos.below()).is(Blocks.SAND) ? pos : null;
    }

    /** Drifting among chorus plants and end rods in the End. */
    public static BlockPos voidMoth(ServerLevel level, BlockPos origin, RandomSource random) {
        if (level.dimension() != Level.END) return null;
        BlockPos pos = besideBlock(level, origin, s -> s.is(Blocks.CHORUS_PLANT) || s.is(Blocks.CHORUS_FLOWER) || s.is(Blocks.END_ROD));
        return pos;
    }
}
