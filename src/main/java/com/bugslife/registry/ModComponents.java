package com.bugslife.registry;

import com.bugslife.BugsLife;
import com.bugslife.bug.BugData;
import net.minecraft.core.component.DataComponentType;
import net.minecraft.core.registries.Registries;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

public final class ModComponents {
    public static final DeferredRegister.DataComponents COMPONENTS =
            DeferredRegister.createDataComponents(Registries.DATA_COMPONENT_TYPE, BugsLife.MODID);

    public static final DeferredHolder<DataComponentType<?>, DataComponentType<BugData>> BUG =
            COMPONENTS.registerComponentType("bug", b -> b.persistent(BugData.CODEC).networkSynchronized(BugData.STREAM_CODEC));

    private ModComponents() {
    }
}
