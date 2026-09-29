package com.bugslife.registry;

import com.bugslife.BugsLife;
import com.bugslife.bug.BugSpecies;
import com.bugslife.item.BugJarItem;
import com.bugslife.item.BugNetItem;
import com.bugslife.item.FieldGuideItem;
import com.bugslife.item.FrassItem;
import com.bugslife.item.HoneydewItem;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.food.FoodProperties;
import com.bugslife.item.ChitinArmorItem;
import com.bugslife.item.ChitinShieldItem;
import net.minecraft.world.item.ArmorItem;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.Rarity;
import net.neoforged.neoforge.common.DeferredSpawnEggItem;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

import java.util.Map;

/**
 * Items. The static initializer must not touch {@link BugSpecies} (BugSpecies refers back to these fields);
 * spawn eggs are registered separately from {@link #registerSpawnEggs()}.
 */
public final class ModItems {
    public static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(BugsLife.MODID);

    // tools
    public static final DeferredItem<BugNetItem> BUG_NET = ITEMS.register("bug_net",
            () -> new BugNetItem(false, new Item.Properties().durability(96)));
    public static final DeferredItem<BugNetItem> SILK_NET = ITEMS.register("silk_net",
            () -> new BugNetItem(true, new Item.Properties().durability(320).rarity(Rarity.UNCOMMON)));
    public static final DeferredItem<BugJarItem> BUG_JAR = ITEMS.register("bug_jar",
            () -> new BugJarItem(new Item.Properties().stacksTo(16)));
    public static final DeferredItem<FieldGuideItem> FIELD_GUIDE = ITEMS.register("field_guide",
            () -> new FieldGuideItem(new Item.Properties().stacksTo(1)));

    // materials
    public static final DeferredItem<Item> SILK = ITEMS.registerSimpleItem("silk");
    public static final DeferredItem<Item> CHITIN = ITEMS.registerSimpleItem("chitin");
    public static final DeferredItem<Item> GLOW_GOO = ITEMS.registerSimpleItem("glow_goo");
    public static final DeferredItem<Item> CICADA_SHELL = ITEMS.registerSimpleItem("cicada_shell");
    public static final DeferredItem<Item> ROYAL_JELLY = ITEMS.registerSimpleItem("royal_jelly", new Item.Properties()
            .rarity(Rarity.RARE).food(new FoodProperties.Builder().nutrition(6).saturationModifier(1.2f).alwaysEdible()
                    .effect(() -> new MobEffectInstance(MobEffects.REGENERATION, 200, 1), 1f)
                    .effect(() -> new MobEffectInstance(MobEffects.ABSORPTION, 1200, 0), 1f).build()));
    public static final DeferredItem<FrassItem> FRASS = ITEMS.register("frass", () -> new FrassItem(new Item.Properties()));
    public static final DeferredItem<HoneydewItem> HONEYDEW = ITEMS.register("honeydew", () -> new HoneydewItem(new Item.Properties()
            .food(new FoodProperties.Builder().nutrition(3).saturationModifier(0.3f).alwaysEdible().fast().build())));

    // food
    public static final DeferredItem<Item> CRUNCHY_GRUB = ITEMS.registerSimpleItem("crunchy_grub", new Item.Properties()
            .food(new FoodProperties.Builder().nutrition(2).saturationModifier(0.1f)
                    .effect(() -> new MobEffectInstance(MobEffects.HUNGER, 200, 0), 0.2f).build()));
    public static final DeferredItem<Item> ROASTED_GRUB = ITEMS.registerSimpleItem("roasted_grub", new Item.Properties()
            .food(new FoodProperties.Builder().nutrition(5).saturationModifier(0.6f).build()));
    public static final DeferredItem<Item> BUG_SKEWER = ITEMS.registerSimpleItem("bug_skewer", new Item.Properties()
            .food(new FoodProperties.Builder().nutrition(11).saturationModifier(0.8f).usingConvertsTo(Items.STICK).build()));
    public static final DeferredItem<Item> CRICKET_COOKIE = ITEMS.registerSimpleItem("cricket_cookie", new Item.Properties()
            .food(new FoodProperties.Builder().nutrition(2).saturationModifier(0.2f).fast()
                    .effect(() -> new MobEffectInstance(MobEffects.MOVEMENT_SPEED, 300, 0), 1f).build()));
    public static final DeferredItem<Item> CANDIED_GRUB = ITEMS.registerSimpleItem("candied_grub", new Item.Properties()
            .food(new FoodProperties.Builder().nutrition(6).saturationModifier(0.7f)
                    .effect(() -> new MobEffectInstance(MobEffects.DIG_SPEED, 1200, 0), 1f).build()));
    public static final DeferredItem<Item> GLOW_JELLY = ITEMS.registerSimpleItem("glow_jelly", new Item.Properties().stacksTo(16)
            .food(new FoodProperties.Builder().nutrition(4).saturationModifier(0.5f).alwaysEdible().usingConvertsTo(Items.BOWL)
                    .effect(() -> new MobEffectInstance(MobEffects.NIGHT_VISION, 2400, 0), 1f)
                    .effect(() -> new MobEffectInstance(MobEffects.GLOWING, 200, 0), 1f).build()));

    // blocks
    public static final DeferredItem<BlockItem> TERRARIUM = ITEMS.registerSimpleBlockItem(ModBlocks.TERRARIUM);
    public static final DeferredItem<BlockItem> FIREFLY_LANTERN = ITEMS.registerSimpleBlockItem(ModBlocks.FIREFLY_LANTERN);
    public static final DeferredItem<BlockItem> REINFORCED_TERRARIUM = ITEMS.registerSimpleBlockItem(ModBlocks.REINFORCED_TERRARIUM);
    public static final DeferredItem<BlockItem> CHITIN_BLOCK = ITEMS.registerSimpleBlockItem(ModBlocks.CHITIN_BLOCK);
    public static final DeferredItem<BlockItem> CHITIN_TILES = ITEMS.registerSimpleBlockItem(ModBlocks.CHITIN_TILES);
    public static final DeferredItem<BlockItem> CHITIN_TILE_STAIRS = ITEMS.registerSimpleBlockItem(ModBlocks.CHITIN_TILE_STAIRS);
    public static final DeferredItem<BlockItem> CHITIN_TILE_SLAB = ITEMS.registerSimpleBlockItem(ModBlocks.CHITIN_TILE_SLAB);
    public static final DeferredItem<BlockItem> SHELL_LAMP = ITEMS.registerSimpleBlockItem(ModBlocks.SHELL_LAMP);

    // chitin gear
    public static final DeferredItem<ChitinArmorItem> CHITIN_HELMET = ITEMS.register("chitin_helmet", () -> new ChitinArmorItem(ModArmorMaterials.CHITIN,
            ArmorItem.Type.HELMET, new Item.Properties().durability(ArmorItem.Type.HELMET.getDurability(18))));
    public static final DeferredItem<ChitinArmorItem> CHITIN_CHESTPLATE = ITEMS.register("chitin_chestplate", () -> new ChitinArmorItem(ModArmorMaterials.CHITIN,
            ArmorItem.Type.CHESTPLATE, new Item.Properties().durability(ArmorItem.Type.CHESTPLATE.getDurability(18))));
    public static final DeferredItem<ChitinArmorItem> CHITIN_LEGGINGS = ITEMS.register("chitin_leggings", () -> new ChitinArmorItem(ModArmorMaterials.CHITIN,
            ArmorItem.Type.LEGGINGS, new Item.Properties().durability(ArmorItem.Type.LEGGINGS.getDurability(18))));
    public static final DeferredItem<ChitinArmorItem> CHITIN_BOOTS = ITEMS.register("chitin_boots", () -> new ChitinArmorItem(ModArmorMaterials.CHITIN,
            ArmorItem.Type.BOOTS, new Item.Properties().durability(ArmorItem.Type.BOOTS.getDurability(18))));
    public static final DeferredItem<ChitinShieldItem> CHITIN_SHIELD = ITEMS.register("chitin_shield",
            () -> new ChitinShieldItem(new Item.Properties().durability(420)));

    // a HashMap, not an EnumMap: BugSpecies may still be initializing when this class loads
    public static final Map<BugSpecies, DeferredItem<DeferredSpawnEggItem>> SPAWN_EGGS = new java.util.HashMap<>();

    public static void registerSpawnEggs() {
        for (BugSpecies species : BugSpecies.values()) {
            SPAWN_EGGS.put(species, ITEMS.register(species.id() + "_spawn_egg", () -> new DeferredSpawnEggItem(
                    ModEntities.get(species), species.eggPrimary(), species.eggSecondary(), new Item.Properties())));
        }
    }

    private ModItems() {
    }
}
