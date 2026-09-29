package com.bugslife.bug;

import com.bugslife.entity.BugEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.BiomeTags;
import net.minecraft.tags.BlockTags;
import net.minecraft.tags.FluidTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.biome.Biomes;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.phys.AABB;
import org.jetbrains.annotations.Nullable;

import java.util.Set;

import static com.bugslife.bug.Habitats.*;

/** Habitat rules for the fifty expansion bugs. Same contract as {@link Habitats}. */
public final class MoreHabitats {
    private MoreHabitats() {
    }

    // ------------------------------------------------------------------ helpers

    private static boolean dusk(ServerLevel level) {
        long t = level.getDayTime() % 24000L;
        return t > 11500 && t < 13800;
    }

    private static boolean dawn(ServerLevel level) {
        long t = level.getDayTime() % 24000L;
        return t > 22500 || t < 1500;
    }

    /** Surface position whose ground matches, or null. */
    @Nullable
    private static BlockPos ground(ServerLevel level, BlockPos origin, Set<Block> floors) {
        BlockPos pos = surface(level, origin);
        if (pos == null) return null;
        return floors.contains(level.getBlockState(pos.below()).getBlock()) ? pos : null;
    }

    /** The bottom of a water column: a water block resting on solid ground, at most maxDepth below the surface. */
    @Nullable
    private static BlockPos waterBottom(ServerLevel level, BlockPos origin, int minDepth, int maxDepth) {
        int top = level.getHeight(Heightmap.Types.WORLD_SURFACE, origin.getX(), origin.getZ()) - 1;
        BlockPos.MutableBlockPos pos = new BlockPos.MutableBlockPos(origin.getX(), top, origin.getZ());
        int depth = 0;
        while (level.getFluidState(pos).is(FluidTags.WATER) && depth <= maxDepth) {
            pos.move(Direction.DOWN);
            depth++;
        }
        if (depth < Math.max(1, minDepth) || depth > maxDepth) return null;
        BlockState below = level.getBlockState(pos);
        if (!below.isFaceSturdy(level, pos, Direction.UP)) return null;
        return pos.above().immutable();
    }

    /** Still water surface: the air block above a water source. */
    @Nullable
    private static BlockPos waterSurface(ServerLevel level, BlockPos origin) {
        int y = level.getHeight(Heightmap.Types.WORLD_SURFACE, origin.getX(), origin.getZ());
        BlockPos water = new BlockPos(origin.getX(), y - 1, origin.getZ());
        if (!level.getFluidState(water).is(FluidTags.WATER) || !level.getFluidState(water).isSource()) return null;
        return level.getBlockState(water.above()).isAir() ? water.above() : null;
    }

    @Nullable
    private static BlockPos airAbove(ServerLevel level, BlockPos pos, RandomSource random, int maxUp) {
        BlockPos air = pos.above(random.nextInt(maxUp + 1));
        return level.getBlockState(air).isAir() ? air : (level.getBlockState(pos).isAir() ? pos : null);
    }

    private static int nearby(ServerLevel level, BlockPos pos, BugSpecies species, double r) {
        return level.getEntitiesOfClass(BugEntity.class, new AABB(pos).inflate(r), b -> b.species() == species).size();
    }

    private static final Set<Block> GRASSY = Set.of(Blocks.GRASS_BLOCK, Blocks.DIRT, Blocks.COARSE_DIRT, Blocks.PODZOL);
    private static final Set<Block> SANDY = Set.of(Blocks.SAND, Blocks.RED_SAND);
    private static final Set<Block> DRY = Set.of(Blocks.SAND, Blocks.RED_SAND, Blocks.TERRACOTTA, Blocks.RED_TERRACOTTA,
            Blocks.ORANGE_TERRACOTTA, Blocks.YELLOW_TERRACOTTA, Blocks.BROWN_TERRACOTTA, Blocks.WHITE_TERRACOTTA,
            Blocks.LIGHT_GRAY_TERRACOTTA, Blocks.COARSE_DIRT);
    private static final Set<Block> ICY = Set.of(Blocks.SNOW_BLOCK, Blocks.POWDER_SNOW, Blocks.ICE, Blocks.PACKED_ICE,
            Blocks.BLUE_ICE, Blocks.STONE, Blocks.CALCITE);
    private static final Set<Block> TRIAL = Set.of(Blocks.TUFF_BRICKS, Blocks.CHISELED_TUFF, Blocks.POLISHED_TUFF,
            Blocks.CHISELED_TUFF_BRICKS, Blocks.WAXED_COPPER_BLOCK, Blocks.WAXED_CUT_COPPER, Blocks.WAXED_CHISELED_COPPER,
            Blocks.WAXED_OXIDIZED_CUT_COPPER, Blocks.WAXED_WEATHERED_CUT_COPPER, Blocks.WAXED_EXPOSED_CUT_COPPER,
            Blocks.WAXED_COPPER_GRATE, Blocks.WAXED_OXIDIZED_COPPER_GRATE, Blocks.TRIAL_SPAWNER, Blocks.VAULT);
    private static final Set<Block> VILLAGE_WALLS = Set.of(Blocks.COBBLESTONE, Blocks.STONE_BRICKS, Blocks.OAK_PLANKS,
            Blocks.SPRUCE_PLANKS, Blocks.OAK_LOG, Blocks.SPRUCE_LOG, Blocks.OAK_FENCE, Blocks.SPRUCE_FENCE, Blocks.SANDSTONE,
            Blocks.SMOOTH_SANDSTONE, Blocks.ACACIA_PLANKS, Blocks.WHITE_TERRACOTTA, Blocks.MOSSY_COBBLESTONE);

    // ================================================================== common

    /** Busy columns on open dirt and grass. */
    public static BlockPos workerAnt(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        BlockPos pos = ground(level, origin, GRASSY);
        if (pos == null) return null;
        var biome = level.getBiome(pos);
        return biome.value().coldEnoughToSnow(pos) || biome.is(BiomeTags.IS_OCEAN) ? null : pos;
    }

    /** Dark nooks at night: under the canopy, and around villages. */
    public static BlockPos earwig(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        BlockPos pos = surface(level, origin);
        if (pos == null || !GRASSY.contains(level.getBlockState(pos.below()).getBlock())) return null;
        if (level.isVillage(pos)) return pos;
        return !level.canSeeSky(pos.above(3)) && random.nextInt(2) == 0 ? pos : null;
    }

    /** Savannas, and anywhere else near fallen logs and dead bushes. */
    public static BlockPos termite(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        BlockPos pos = surface(level, origin);
        if (pos == null) return null;
        if (level.getBiome(pos).is(BiomeTags.IS_SAVANNA) && GRASSY.contains(level.getBlockState(pos.below()).getBlock())) return pos;
        return nearBlock(level, pos, 1, 1, s -> s.is(BlockTags.LOGS) || s.is(Blocks.DEAD_BUSH)) && random.nextInt(3) == 0 ? pos : null;
    }

    /** Damp woodland floors after dark. */
    public static BlockPos millipede(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        BlockPos pos = floor(level, origin, 10);
        if (pos == null) return null;
        Block below = level.getBlockState(pos.below()).getBlock();
        if (PILL_BUG_FLOORS.contains(below)) return pos;
        var biome = level.getBiome(pos);
        return (biome.is(BiomeTags.IS_FOREST) || biome.is(BiomeTags.IS_JUNGLE)) && GRASSY.contains(below) && random.nextInt(3) == 0 ? pos : null;
    }

    /** On the beds of rivers and shallow streams. */
    public static BlockPos caddisflyLarva(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level) || !level.getBiome(origin).is(BiomeTags.IS_RIVER)) return null;
        return waterBottom(level, origin, 1, 5);
    }

    /** Over swamps and marshy water at night. */
    public static BlockPos mosquito(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        var biome = level.getBiome(origin);
        boolean swamp = biome.is(Biomes.SWAMP) || biome.is(Biomes.MANGROVE_SWAMP);
        BlockPos pos = surface(level, origin);
        if (pos == null) {
            pos = waterSurface(level, origin);
        }
        if (pos == null) return null;
        if (!swamp && !(nearBlock(level, pos, 3, 2, s -> s.getFluidState().is(FluidTags.WATER)) && random.nextInt(6) == 0)) return null;
        return airAbove(level, pos, random, 2);
    }

    /** Dancing over rivers at dusk. */
    public static BlockPos mayfly(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level) || !dusk(level)) return null;
        BlockPos pos = waterSurface(level, origin);
        if (pos == null || !(level.getBiome(pos).is(BiomeTags.IS_RIVER) || random.nextInt(4) == 0)) return null;
        return airAbove(level, pos, random, 3);
    }

    /** Sunny plains, savannas and meadows. */
    public static BlockPos grasshopper(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        BlockPos pos = ground(level, origin, Set.of(Blocks.GRASS_BLOCK));
        if (pos == null) return null;
        var biome = level.getBiome(pos);
        return biome.is(Biomes.PLAINS) || biome.is(Biomes.SUNFLOWER_PLAINS) || biome.is(BiomeTags.IS_SAVANNA) || biome.is(Biomes.MEADOW) ? pos : null;
    }

    /** On snow, even in the coldest weather. */
    public static BlockPos springtail(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        BlockPos pos = surface(level, origin);
        if (pos == null) return null;
        boolean snow = level.getBlockState(pos).is(Blocks.SNOW) || level.getBlockState(pos.below()).is(Blocks.SNOW_BLOCK);
        return snow ? pos : null;
    }

    /** Spinning on still ponds and slow rivers. */
    public static BlockPos whirligig(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        BlockPos pos = waterSurface(level, origin);
        if (pos == null) return null;
        var biome = level.getBiome(pos);
        if (biome.is(BiomeTags.IS_OCEAN) || biome.value().coldEnoughToSnow(pos)) return null;
        return biome.is(BiomeTags.IS_RIVER) || biome.is(Biomes.SWAMP) || random.nextInt(3) == 0 ? pos : null;
    }

    /** Farms and vegetable patches. */
    public static BlockPos stinkBug(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        BlockPos pos = surface(level, origin);
        if (pos == null) return null;
        return nearBlock(level, pos, 2, 1, s -> s.is(BlockTags.CROPS)) ? pos : null;
    }

    // ================================================================== uncommon

    /** Beside trunks, fences and bushes at dusk and night. */
    public static BlockPos orbWeaver(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        BlockPos pos = besideBlock(level, origin, s -> s.is(BlockTags.LOGS) || s.is(BlockTags.FENCES));
        return pos != null && level.canSeeSky(pos) ? pos : null;
    }

    /** In long grass and ferns of forests and taigas. */
    public static BlockPos tick(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        BlockPos pos = surface(level, origin);
        if (pos == null) return null;
        BlockState here = level.getBlockState(pos);
        boolean tall = here.is(Blocks.SHORT_GRASS) || here.is(Blocks.TALL_GRASS) || here.is(Blocks.FERN) || here.is(Blocks.LARGE_FERN);
        var biome = level.getBiome(pos);
        return tall && (biome.is(BiomeTags.IS_TAIGA) || biome.is(BiomeTags.IS_FOREST)) ? pos : null;
    }

    /** Dark caves and stronghold corridors, hunting silverfish. */
    public static BlockPos centipede(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level) || origin.getY() > 50) return null;
        BlockPos pos = floor(level, origin, 10);
        if (pos == null || !dark(level, pos, 4)) return null;
        Block below = level.getBlockState(pos.below()).getBlock();
        if (below == Blocks.STONE_BRICKS || below == Blocks.MOSSY_STONE_BRICKS || below == Blocks.CRACKED_STONE_BRICKS) return pos;
        return CAVE_FLOORS.contains(below) && random.nextInt(3) == 0 ? pos : null;
    }

    /** Sunny walls and fences, especially in villages. */
    public static BlockPos jumpingSpider(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        BlockPos pos = besideBlock(level, origin, s -> VILLAGE_WALLS.contains(s.getBlock()));
        return pos != null && level.canSeeSky(pos) && level.getBlockState(pos.below()).isSolid() ? pos : null;
    }

    /** Deserts and badlands. */
    public static BlockPos honeypotAnt(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        BlockPos pos = ground(level, origin, DRY);
        if (pos == null) return null;
        var biome = level.getBiome(pos);
        return biome.is(Biomes.DESERT) || biome.is(BiomeTags.IS_BADLANDS) ? pos : null;
    }

    /** Buried in the sand of deserts and beaches. */
    public static BlockPos antlion(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        BlockPos pos = ground(level, origin, SANDY);
        if (pos == null) return null;
        var biome = level.getBiome(pos);
        return biome.is(Biomes.DESERT) || biome.is(BiomeTags.IS_BEACH) || biome.is(BiomeTags.IS_BADLANDS) ? pos : null;
    }

    /** Beside bookshelves: libraries, villages, strongholds and mansions. */
    public static BlockPos bookworm(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        BlockPos pos = besideBlock(level, origin, s -> s.is(Blocks.BOOKSHELF) || s.is(Blocks.CHISELED_BOOKSHELF) || s.is(Blocks.LECTERN));
        return pos != null && level.getBlockState(pos.below()).isSolid() ? pos : null;
    }

    /** Clinging to acacia trunks in the savanna heat. */
    public static BlockPos cicada(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        return besideBlock(level, origin, s -> s.is(Blocks.ACACIA_LOG));
    }

    /** Under the forest canopy at night. */
    public static BlockPos katydid(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        BlockPos pos = ground(level, origin, GRASSY);
        if (pos == null) return null;
        var biome = level.getBiome(pos);
        return (biome.is(BiomeTags.IS_FOREST) || biome.is(BiomeTags.IS_JUNGLE)) && nearBlock(level, pos, 3, 4, s -> s.is(BlockTags.LEAVES)) ? pos : null;
    }

    /** Flower meadows and flower forests by day. */
    public static BlockPos hawkMoth(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        BlockPos pos = surface(level, origin);
        if (pos == null) return null;
        var biome = level.getBiome(pos);
        boolean meadow = biome.is(Biomes.MEADOW) || biome.is(Biomes.FLOWER_FOREST) || biome.is(Biomes.SUNFLOWER_PLAINS);
        return meadow && nearBlock(level, pos, 2, 1, s -> s.is(BlockTags.FLOWERS)) ? airAbove(level, pos, random, 2) : null;
    }

    /** Only in cherry groves. */
    public static BlockPos sakuraMoth(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        BlockPos pos = surface(level, origin);
        if (pos == null || !level.getBiome(pos).is(Biomes.CHERRY_GROVE)) return null;
        return airAbove(level, pos, random, 3);
    }

    /** Around village roofs by day. */
    public static BlockPos paperWasp(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        BlockPos pos = surface(level, origin);
        if (pos == null || !level.isVillage(pos)) return null;
        return airAbove(level, pos, random, 4);
    }

    /** Swarms over savannas and dry plains. */
    public static BlockPos locust(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        BlockPos pos = surface(level, origin);
        if (pos == null) return null;
        var biome = level.getBiome(pos);
        if (!(biome.is(BiomeTags.IS_SAVANNA) || biome.is(Biomes.DESERT) && random.nextInt(3) == 0)) return null;
        return random.nextInt(4) == 0 ? airAbove(level, pos, random, 3) : null;
    }

    /** Waiting motionless among the flowers. */
    public static BlockPos prayingMantis(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        BlockPos pos = surface(level, origin);
        if (pos == null) return null;
        return nearBlock(level, pos, 2, 1, s -> s.is(BlockTags.FLOWERS)) && random.nextInt(2) == 0 ? pos : null;
    }

    /** Woodland floors at night. */
    public static BlockPos bombardier(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        BlockPos pos = ground(level, origin, GRASSY);
        if (pos == null || !level.getBiome(pos).is(BiomeTags.IS_FOREST)) return null;
        return random.nextInt(2) == 0 ? pos : null;
    }

    /** Underwater in ponds, lakes and swamps. */
    public static BlockPos divingBeetle(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        var biome = level.getBiome(origin);
        if (biome.is(BiomeTags.IS_OCEAN) || biome.is(BiomeTags.IS_DEEP_OCEAN) || biome.is(BiomeTags.IS_RIVER) && random.nextBoolean()) return null;
        BlockPos bottom = waterBottom(level, origin, 2, 8);
        return bottom != null ? bottom.above() : null;
    }

    /** Moist soil near water, after dark. */
    public static BlockPos moleCricket(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        BlockPos pos = ground(level, origin, GRASSY);
        if (pos == null) return null;
        return nearBlock(level, pos, 4, 1, s -> s.getFluidState().is(FluidTags.WATER)) ? pos : null;
    }

    /** Desert dunes; they fog-bask at dawn. */
    public static BlockPos darklingBeetle(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        BlockPos pos = ground(level, origin, DRY);
        if (pos == null) return null;
        var biome = level.getBiome(pos);
        return biome.is(Biomes.DESERT) || biome.is(BiomeTags.IS_BADLANDS) ? pos : null;
    }

    // ================================================================== rare

    /** Deserts and badlands at night. */
    public static BlockPos scorpion(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        BlockPos pos = ground(level, origin, DRY);
        if (pos == null) return null;
        var biome = level.getBiome(pos);
        return biome.is(Biomes.DESERT) || biome.is(BiomeTags.IS_BADLANDS) ? pos : null;
    }

    /** Badlands and savannas at night. */
    public static BlockPos tarantula(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        BlockPos pos = surface(level, origin);
        if (pos == null) return null;
        var biome = level.getBiome(pos);
        return biome.is(BiomeTags.IS_BADLANDS) || biome.is(BiomeTags.IS_SAVANNA) ? pos : null;
    }

    /** High, frozen peaks and ice spikes. */
    public static BlockPos iceCrawler(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        BlockPos pos = surface(level, origin);
        if (pos == null) return null;
        var biome = level.getBiome(pos);
        boolean frozen = biome.is(Biomes.FROZEN_PEAKS) || biome.is(Biomes.JAGGED_PEAKS) || biome.is(Biomes.SNOWY_SLOPES)
                || biome.is(Biomes.ICE_SPIKES) || biome.is(Biomes.GROVE);
        if (!frozen) return null;
        Block below = level.getBlockState(pos.below()).getBlock();
        return ICY.contains(below) || level.getBlockState(pos).is(Blocks.SNOW) ? pos : null;
    }

    /** The floor of the deep ocean. */
    public static BlockPos giantIsopod(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level) || !level.getBiome(origin).is(BiomeTags.IS_DEEP_OCEAN)) return null;
        return waterBottom(level, origin, 12, 60);
    }

    /** Woodland canopies, but only under a full moon. */
    public static BlockPos lunaMoth(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level) || level.getMoonPhase() != 0) return null;
        BlockPos pos = besideBlock(level, origin, s -> s.is(BlockTags.LEAVES));
        return pos != null && level.canSeeSky(pos) ? pos : null;
    }

    /** Sunny jungle clearings. */
    public static BlockPos morpho(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level) || !level.getBiome(origin).is(BiomeTags.IS_JUNGLE)) return null;
        BlockPos pos = surface(level, origin);
        return pos == null ? null : airAbove(level, pos, random, 3);
    }

    /** Dark forests and jungles at dusk and night. */
    public static BlockPos owlButterfly(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        var biome = level.getBiome(origin);
        if (!(biome.is(Biomes.DARK_FOREST) || biome.is(BiomeTags.IS_JUNGLE))) return null;
        BlockPos pos = surface(level, origin);
        return pos == null ? null : airAbove(level, pos, random, 2);
    }

    /** Jungle and bamboo leaves - good luck spotting it. */
    public static BlockPos leafInsect(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level) || !level.getBiome(origin).is(BiomeTags.IS_JUNGLE)) return null;
        return besideBlock(level, origin, s -> s.is(Blocks.JUNGLE_LEAVES) || s.is(Blocks.BAMBOO));
    }

    /** Forest floors at night, headlights on. */
    public static BlockPos clickBeetle(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        BlockPos pos = ground(level, origin, GRASSY);
        if (pos == null) return null;
        var biome = level.getBiome(pos);
        return biome.is(BiomeTags.IS_FOREST) || biome.is(BiomeTags.IS_JUNGLE) ? pos : null;
    }

    /** Far out on the open ocean. */
    public static BlockPos seaSkater(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        var biome = level.getBiome(origin);
        if (!(biome.is(BiomeTags.IS_OCEAN) || biome.is(BiomeTags.IS_DEEP_OCEAN))) return null;
        BlockPos pos = waterSurface(level, origin);
        if (pos == null) return null;
        // no land within 8 blocks in any direction
        for (Direction d : Direction.Plane.HORIZONTAL) {
            BlockPos probe = pos.relative(d, 8).below();
            if (!level.getFluidState(probe).is(FluidTags.WATER)) return null;
        }
        return pos;
    }

    /** Mushroom islands, on mycelium. */
    public static BlockPos mushroomBeetle(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level)) return null;
        return ground(level, origin, Set.of(Blocks.MYCELIUM));
    }

    /** Only while it is raining. */
    public static BlockPos rainBeetle(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level) || !level.isRaining()) return null;
        BlockPos pos = ground(level, origin, GRASSY);
        return pos != null && level.isRainingAt(pos) ? pos : null;
    }

    // ================================================================== epic

    /** Beside jungle leaves on the darkest nights. */
    public static BlockPos atlasMoth(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level) || !level.getBiome(origin).is(BiomeTags.IS_JUNGLE)) return null;
        return besideBlock(level, origin, s -> s.is(Blocks.JUNGLE_LEAVES));
    }

    /** Soul sand valleys in the Nether. */
    public static BlockPos soulMoth(ServerLevel level, BlockPos origin, RandomSource random) {
        if (level.dimension() != Level.NETHER) return null;
        BlockPos pos = floor(level, origin, 12);
        if (pos == null) return null;
        Block below = level.getBlockState(pos.below()).getBlock();
        return below == Blocks.SOUL_SAND || below == Blocks.SOUL_SOIL ? airAbove(level, pos, random, 3) : null;
    }

    /** The tuff and copper halls of trial chambers. */
    public static BlockPos gustMoth(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level) || origin.getY() > 30) return null;
        BlockPos pos = besideBlock(level, origin, s -> TRIAL.contains(s.getBlock()));
        return pos != null && !level.canSeeSky(pos) ? pos : null;
    }

    /** Among the purpur of End cities. */
    public static BlockPos shulkerMite(ServerLevel level, BlockPos origin, RandomSource random) {
        if (level.dimension() != Level.END) return null;
        return besideBlock(level, origin, s -> s.is(Blocks.PURPUR_BLOCK) || s.is(Blocks.PURPUR_PILLAR) || s.is(Blocks.PURPUR_STAIRS));
    }

    /** End stone beneath the chorus. */
    public static BlockPos chorusWeevil(ServerLevel level, BlockPos origin, RandomSource random) {
        if (level.dimension() != Level.END) return null;
        BlockPos pos = floor(level, origin, 10);
        if (pos == null || !level.getBlockState(pos.below()).is(Blocks.END_STONE)) return null;
        return nearBlock(level, pos, 3, 2, s -> s.is(Blocks.CHORUS_PLANT) || s.is(Blocks.CHORUS_FLOWER)) ? pos : null;
    }

    /** The silent Deep Dark. */
    public static BlockPos echoMoth(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level) || origin.getY() > 0 || !level.getBiome(origin).is(Biomes.DEEP_DARK)) return null;
        BlockPos pos = floor(level, origin, 10);
        return pos == null ? null : airAbove(level, pos, random, 3);
    }

    // ================================================================== legendary

    /** Found only where a colony of worker ants is already marching. */
    public static BlockPos queenAnt(ServerLevel level, BlockPos origin, RandomSource random) {
        BlockPos pos = workerAnt(level, origin, random);
        if (pos == null || nearby(level, pos, BugSpecies.WORKER_ANT, 16) < 4 || nearby(level, pos, BugSpecies.QUEEN_ANT, 48) > 0) return null;
        return pos;
    }

    /** High ground in a thunderstorm. */
    public static BlockPos stormBeetle(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level) || !level.isThundering()) return null;
        BlockPos pos = surface(level, origin);
        return pos != null && pos.getY() > 70 && level.canSeeSky(pos) ? pos : null;
    }

    /** Inside amethyst geodes. */
    public static BlockPos crystalBeetle(ServerLevel level, BlockPos origin, RandomSource random) {
        if (!overworld(level) || origin.getY() > 40) return null;
        BlockPos pos = floor(level, origin, 8);
        if (pos == null) return null;
        Block below = level.getBlockState(pos.below()).getBlock();
        return below == Blocks.AMETHYST_BLOCK || below == Blocks.BUDDING_AMETHYST || below == Blocks.CALCITE ? pos : null;
    }
}
