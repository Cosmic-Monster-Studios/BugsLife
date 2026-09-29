package com.bugslife;

import com.bugslife.bug.BugSpecies;
import com.bugslife.entity.BugEntity;
import com.bugslife.network.Network;
import com.bugslife.registry.ModAttachments;
import com.bugslife.registry.ModBlockEntities;
import com.bugslife.registry.ModBlocks;
import com.bugslife.registry.ModComponents;
import com.bugslife.registry.ModEntities;
import com.bugslife.registry.ModItems;
import com.bugslife.registry.ModTabs;
import com.bugslife.registry.ModTriggers;
import com.bugslife.spawn.BugSpawner;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.config.ModConfig;
import net.neoforged.neoforge.capabilities.Capabilities;
import net.neoforged.neoforge.capabilities.RegisterCapabilitiesEvent;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.entity.EntityAttributeCreationEvent;

@Mod(BugsLife.MODID)
public class BugsLife {
    public static final String MODID = "bugslife";

    public BugsLife(IEventBus modBus, ModContainer container) {
        ModComponents.COMPONENTS.register(modBus);
        com.bugslife.registry.ModArmorMaterials.ARMOR_MATERIALS.register(modBus);
        ModEntities.ENTITIES.register(modBus);
        ModBlocks.BLOCKS.register(modBus);
        ModItems.registerSpawnEggs();
        ModItems.ITEMS.register(modBus);
        ModBlockEntities.BLOCK_ENTITIES.register(modBus);
        ModTabs.TABS.register(modBus);
        ModTriggers.TRIGGERS.register(modBus);
        ModAttachments.ATTACHMENTS.register(modBus);

        modBus.addListener(this::onAttributes);
        modBus.addListener(this::onCapabilities);
        modBus.addListener(Network::register);

        container.registerConfig(ModConfig.Type.COMMON, Config.SPEC);

        NeoForge.EVENT_BUS.register(BugSpawner.class);
        NeoForge.EVENT_BUS.register(com.bugslife.bug.JournalEvents.class);
        NeoForge.EVENT_BUS.register(com.bugslife.entity.SpecialBehaviors.class);
        NeoForge.EVENT_BUS.register(com.bugslife.item.ChitinGear.class);
    }

    private void onAttributes(EntityAttributeCreationEvent event) {
        for (BugSpecies species : BugSpecies.values()) {
            event.put(ModEntities.get(species).get(), BugEntity.createAttributes(species).build());
        }
    }

    private void onCapabilities(RegisterCapabilitiesEvent event) {
        event.registerBlockEntity(Capabilities.ItemHandler.BLOCK, ModBlockEntities.TERRARIUM.get(),
                (be, side) -> be.getOutputHandler());
    }

    public static ResourceLocation id(String path) {
        return ResourceLocation.fromNamespaceAndPath(MODID, path);
    }
}
