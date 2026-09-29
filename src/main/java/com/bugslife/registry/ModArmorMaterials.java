package com.bugslife.registry;

import com.bugslife.BugsLife;
import net.minecraft.Util;
import net.minecraft.core.registries.Registries;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.ArmorMaterial;
import net.minecraft.world.item.crafting.Ingredient;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

import java.util.EnumMap;
import java.util.List;

public final class ModArmorMaterials {
    public static final DeferredRegister<ArmorMaterial> ARMOR_MATERIALS = DeferredRegister.create(Registries.ARMOR_MATERIAL, BugsLife.MODID);

    /** Beetle-shell armour: tougher than leather, lighter than iron (12 armour points for the set). */
    public static final DeferredHolder<ArmorMaterial, ArmorMaterial> CHITIN = ARMOR_MATERIALS.register("chitin", () -> new ArmorMaterial(
            Util.make(new EnumMap<>(ArmorItem.Type.class), m -> {
                m.put(ArmorItem.Type.BOOTS, 1);
                m.put(ArmorItem.Type.LEGGINGS, 4);
                m.put(ArmorItem.Type.CHESTPLATE, 5);
                m.put(ArmorItem.Type.HELMET, 2);
                m.put(ArmorItem.Type.BODY, 5);
            }),
            14, SoundEvents.ARMOR_EQUIP_TURTLE, () -> Ingredient.of(ModItems.CHITIN.get()),
            List.of(new ArmorMaterial.Layer(BugsLife.id("chitin"))), 0.0f, 0.0f));

    private ModArmorMaterials() {
    }
}
