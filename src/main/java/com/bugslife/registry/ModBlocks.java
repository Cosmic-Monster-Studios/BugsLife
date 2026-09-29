package com.bugslife.registry;

import com.bugslife.BugsLife;
import com.bugslife.block.FireflyLanternBlock;
import com.bugslife.block.TerrariumBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SlabBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.StairBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.minecraft.world.level.material.PushReaction;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredRegister;

public final class ModBlocks {
    public static final DeferredRegister.Blocks BLOCKS = DeferredRegister.createBlocks(BugsLife.MODID);

    public static final DeferredBlock<TerrariumBlock> TERRARIUM = BLOCKS.register("terrarium", () -> new TerrariumBlock(
            BlockBehaviour.Properties.of().mapColor(MapColor.NONE).strength(0.6f).sound(SoundType.GLASS).noOcclusion()
                    .isViewBlocking((s, l, p) -> false).isSuffocating((s, l, p) -> false)
                    .lightLevel(s -> s.getValue(TerrariumBlock.LIGHT))));

    public static final DeferredBlock<FireflyLanternBlock> FIREFLY_LANTERN = BLOCKS.register("firefly_lantern", () -> new FireflyLanternBlock(
            BlockBehaviour.Properties.of().mapColor(MapColor.METAL).forceSolidOn().strength(3.5f).sound(SoundType.LANTERN)
                    .lightLevel(s -> 15).noOcclusion().pushReaction(PushReaction.DESTROY)));

    public static final DeferredBlock<TerrariumBlock> REINFORCED_TERRARIUM = BLOCKS.register("reinforced_terrarium", () -> new TerrariumBlock(
            BlockBehaviour.Properties.of().mapColor(MapColor.NONE).strength(1.5f).sound(SoundType.GLASS).noOcclusion()
                    .isViewBlocking((s, l, p) -> false).isSuffocating((s, l, p) -> false)
                    .lightLevel(s -> s.getValue(TerrariumBlock.LIGHT)), 8, 1.25f));

    private static BlockBehaviour.Properties chitin() {
        return BlockBehaviour.Properties.of().mapColor(MapColor.TERRACOTTA_BROWN).strength(1.5f, 4.0f)
                .sound(SoundType.BONE_BLOCK).requiresCorrectToolForDrops();
    }

    public static final DeferredBlock<Block> CHITIN_BLOCK = BLOCKS.register("chitin_block", () -> new Block(chitin()));
    public static final DeferredBlock<Block> CHITIN_TILES = BLOCKS.register("chitin_tiles", () -> new Block(chitin()));
    public static final DeferredBlock<StairBlock> CHITIN_TILE_STAIRS = BLOCKS.register("chitin_tile_stairs",
            () -> new StairBlock(CHITIN_TILES.get().defaultBlockState(), chitin()));
    public static final DeferredBlock<SlabBlock> CHITIN_TILE_SLAB = BLOCKS.register("chitin_tile_slab", () -> new SlabBlock(chitin()));
    public static final DeferredBlock<Block> SHELL_LAMP = BLOCKS.register("shell_lamp", () -> new Block(chitin().lightLevel(s -> 15)));

    private ModBlocks() {
    }
}
