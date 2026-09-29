package com.bugslife.registry;

import com.bugslife.BugsLife;
import com.bugslife.block.TerrariumBlockEntity;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

public final class ModBlockEntities {
    public static final DeferredRegister<BlockEntityType<?>> BLOCK_ENTITIES =
            DeferredRegister.create(Registries.BLOCK_ENTITY_TYPE, BugsLife.MODID);

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<TerrariumBlockEntity>> TERRARIUM =
            BLOCK_ENTITIES.register("terrarium", () -> BlockEntityType.Builder.of(TerrariumBlockEntity::new, ModBlocks.TERRARIUM.get(), ModBlocks.REINFORCED_TERRARIUM.get()).build(null));

    private ModBlockEntities() {
    }
}
