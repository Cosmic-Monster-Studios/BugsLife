package com.bugslife.registry;

import com.bugslife.BugsLife;
import com.bugslife.bug.BugData;
import com.bugslife.bug.BugSpecies;
import com.bugslife.item.BugJarItem;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

public final class ModTabs {
    public static final DeferredRegister<CreativeModeTab> TABS = DeferredRegister.create(Registries.CREATIVE_MODE_TAB, BugsLife.MODID);

    public static final DeferredHolder<CreativeModeTab, CreativeModeTab> MAIN = TABS.register("main", () -> CreativeModeTab.builder()
            .title(Component.translatable("itemGroup.bugslife"))
            .icon(() -> BugJarItem.filled(new BugData(BugSpecies.LADYBUG, false, false)))
            .displayItems((params, out) -> {
                out.accept(ModItems.FIELD_GUIDE.get());
                out.accept(ModItems.BUG_NET.get());
                out.accept(ModItems.SILK_NET.get());
                out.accept(ModItems.BUG_JAR.get());
                out.accept(ModItems.TERRARIUM.get());
                out.accept(ModItems.REINFORCED_TERRARIUM.get());
                out.accept(ModItems.FIREFLY_LANTERN.get());
                out.accept(ModItems.CHITIN_HELMET.get());
                out.accept(ModItems.CHITIN_CHESTPLATE.get());
                out.accept(ModItems.CHITIN_LEGGINGS.get());
                out.accept(ModItems.CHITIN_BOOTS.get());
                out.accept(ModItems.CHITIN_SHIELD.get());
                out.accept(ModItems.CHITIN_BLOCK.get());
                out.accept(ModItems.CHITIN_TILES.get());
                out.accept(ModItems.CHITIN_TILE_STAIRS.get());
                out.accept(ModItems.CHITIN_TILE_SLAB.get());
                out.accept(ModItems.SHELL_LAMP.get());
                out.accept(ModItems.SILK.get());
                out.accept(ModItems.CHITIN.get());
                out.accept(ModItems.GLOW_GOO.get());
                out.accept(ModItems.HONEYDEW.get());
                out.accept(ModItems.FRASS.get());
                out.accept(ModItems.CICADA_SHELL.get());
                out.accept(ModItems.ROYAL_JELLY.get());
                out.accept(ModItems.CRUNCHY_GRUB.get());
                out.accept(ModItems.ROASTED_GRUB.get());
                out.accept(ModItems.BUG_SKEWER.get());
                out.accept(ModItems.CRICKET_COOKIE.get());
                out.accept(ModItems.CANDIED_GRUB.get());
                out.accept(ModItems.GLOW_JELLY.get());
                for (BugSpecies species : BugSpecies.values()) {
                    out.accept(BugJarItem.filled(new BugData(species, false, false)));
                }
                for (BugSpecies species : BugSpecies.values()) {
                    out.accept(new ItemStack(ModItems.SPAWN_EGGS.get(species).get()));
                }
            })
            .build());

    private ModTabs() {
    }
}
