package com.bugslife.bug;

import com.bugslife.registry.ModItems;
import com.mojang.serialization.Codec;
import io.netty.buffer.ByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.tags.ItemTags;
import net.minecraft.util.StringRepresentable;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.ItemLike;

import java.util.IdentityHashMap;
import java.util.Locale;
import java.util.Map;
import java.util.function.Supplier;

import static com.bugslife.bug.BugRarity.*;
import static com.bugslife.bug.Movement.*;

/**
 * Every bug in the mod. Model, animation and texture files are named after {@link #id()}.
 */
public enum BugSpecies implements StringRepresentable {
    // ------------------------------------------------------------------ common
    LADYBUG(p(COMMON, CLIMB).size(0.3f, 0.25f, 0.8f).health(2).speed(0.22f)
            .food(() -> Ingredient.of(Items.SWEET_BERRIES)).product(ModItems.FRASS, 1)
            .habitat(Habitats::ladybug, SpawnTime.DAY).group(1, 3).anims(true, true, false).eggs(0xD4251C, 0x1B1A1F)),
    APHID(p(COMMON, CRAWL).size(0.3f, 0.2f, 0.55f).health(1).speed(0.15f)
            .food(() -> Ingredient.of(Items.WHEAT)).product(ModItems.HONEYDEW, 1)
            .habitat(Habitats::aphid, SpawnTime.ANY).group(2, 5).anims(true, false, false).eggs(0x9AD65C, 0x4D8A2A)),
    FIREFLY(p(COMMON, FLY).size(0.3f, 0.25f, 0.7f).health(2).speed(0.2f).fly(0.35f)
            .food(() -> Ingredient.of(Items.SUGAR)).product(ModItems.GLOW_GOO, 1)
            .habitat(Habitats::firefly, SpawnTime.NIGHT).group(3, 7).anims(true, true, false).glow().light(10)
            .eggs(0x2F2826, 0xE9F76C)),
    CRICKET(p(COMMON, HOP).size(0.35f, 0.3f, 0.75f).health(2).speed(0.2f)
            .food(() -> Ingredient.of(Items.WHEAT_SEEDS)).product(ModItems.FRASS, 1)
            .habitat(Habitats::cricket, SpawnTime.NIGHT).group(1, 3).anims(true, false, true).action("chirp")
            .eggs(0x3A2A1F, 0x6B4A2C)),
    PILL_BUG(p(COMMON, CRAWL).size(0.35f, 0.25f, 0.75f).health(3).speed(0.14f)
            .food(() -> Ingredient.of(Items.BROWN_MUSHROOM)).product(ModItems.FRASS, 1)
            .habitat(Habitats::pillBug, SpawnTime.ANY).group(1, 3).anims(true, false, false).extra("roll")
            .eggs(0x5F6772, 0x8A939E)),
    WATER_STRIDER(p(COMMON, SKATE).size(0.5f, 0.2f, 0.7f).health(2).speed(0.25f)
            .food(() -> Ingredient.of(ModItems.CRUNCHY_GRUB.get())).product(ModItems.FRASS, 1)
            .habitat(Habitats::waterStrider, SpawnTime.DAY).group(1, 3).anims(true, false, false).translucent()
            .eggs(0x35332E, 0x8A8474)),
    // ------------------------------------------------------------------ uncommon
    MONARCH(p(UNCOMMON, FLY).size(0.4f, 0.3f, 0.75f).health(2).speed(0.18f).fly(0.3f)
            .food(() -> Ingredient.of(ItemTags.SMALL_FLOWERS)).product(ModItems.HONEYDEW, 1)
            .habitat(Habitats::monarch, SpawnTime.DAY).group(1, 2).anims(false, true, false).eggs(0xF08A1C, 0x171313)),
    SILK_MOTH(p(UNCOMMON, FLY).size(0.4f, 0.35f, 0.7f).health(3).speed(0.18f).fly(0.28f)
            .food(() -> Ingredient.of(ItemTags.LEAVES)).product(ModItems.SILK, 1)
            .habitat(Habitats::silkMoth, SpawnTime.NIGHT).group(1, 2).anims(true, true, false).eggs(0xEFE6D2, 0x9A7D52)),
    DRAGONFLY(p(UNCOMMON, FLY).size(0.45f, 0.3f, 0.65f).health(3).speed(0.25f).fly(0.6f)
            .food(() -> Ingredient.of(ModItems.CRUNCHY_GRUB.get())).product(ModItems.CHITIN, 1)
            .habitat(Habitats::dragonfly, SpawnTime.DAY).group(1, 2).anims(false, true, false).translucent()
            .eggs(0x2F7FD6, 0x3EA36B)),
    DUNG_BEETLE(p(UNCOMMON, CRAWL).size(0.45f, 0.4f, 0.6f).health(4).speed(0.18f)
            .food(() -> Ingredient.of(ModItems.FRASS.get())).product(ModItems.FRASS, 2)
            .habitat(Habitats::dungBeetle, SpawnTime.DAY).group(1, 2).anims(true, false, false).eggs(0x231D1A, 0x6B4A2B)),
    CAVE_WETA(p(UNCOMMON, HOP).size(0.45f, 0.4f, 0.65f).health(4).speed(0.22f)
            .food(() -> Ingredient.of(Items.RED_MUSHROOM)).product(ModItems.CHITIN, 1)
            .habitat(Habitats::caveWeta, SpawnTime.ANY).group(1, 2).anims(true, false, true).eggs(0xC9B391, 0x7A6448)),
    // ------------------------------------------------------------------ rare
    WALKING_STICK(p(RARE, CLIMB).size(0.4f, 0.35f, 0.8f).health(3).speed(0.12f)
            .food(() -> Ingredient.of(ItemTags.LEAVES)).product(() -> Items.STICK, 2)
            .habitat(Habitats::walkingStick, SpawnTime.ANY).group(1, 1).anims(true, false, false).eggs(0x7C6A42, 0x5A4B2A)),
    JEWEL_BEETLE(p(RARE, CLIMB).size(0.3f, 0.25f, 0.8f).health(3).speed(0.2f)
            .food(() -> Ingredient.of(ModItems.HONEYDEW.get())).product(ModItems.CHITIN, 1).bonus(() -> Items.EMERALD, 0.08f)
            .habitat(Habitats::jewelBeetle, SpawnTime.DAY).group(1, 1).anims(true, true, false).eggs(0x23B86E, 0xC9452F)),
    STAG_BEETLE(p(RARE, CLIMB).size(0.55f, 0.4f, 0.65f).health(6).speed(0.16f)
            .food(() -> Ingredient.of(Items.APPLE)).product(ModItems.CHITIN, 1)
            .habitat(Habitats::stagBeetle, SpawnTime.NIGHT).group(1, 2).anims(true, false, false).action("spar")
            .eggs(0x4A2616, 0x7C3A1F)),
    GLOWWORM(p(RARE, HANG).size(0.35f, 0.95f, 0.8f).health(2).speed(0f)
            .food(() -> Ingredient.of(Items.GLOW_BERRIES)).product(ModItems.GLOW_GOO, 1).bonus(ModItems.SILK, 0.3f)
            .habitat(Habitats::glowworm, SpawnTime.ANY).group(2, 4).anims(false, false, false).glow().translucent().light(12)
            .eggs(0xD8E4CF, 0x8FF0FF)),
    // ------------------------------------------------------------------ epic
    HERCULES_BEETLE(p(EPIC, CLIMB).size(0.8f, 0.55f, 0.85f).health(10).speed(0.15f)
            .food(() -> Ingredient.of(Items.MELON_SLICE)).product(ModItems.CHITIN, 2)
            .habitat(Habitats::herculesBeetle, SpawnTime.NIGHT).group(1, 1).anims(true, false, false).action("horn")
            .eggs(0xB9A766, 0x16130F)),
    EMBER_BEETLE(p(EPIC, CRAWL).size(0.45f, 0.35f, 0.75f).health(6).speed(0.2f)
            .food(() -> Ingredient.of(Items.NETHER_WART)).product(() -> Items.BLAZE_POWDER, 1)
            .habitat(Habitats::emberBeetle, SpawnTime.ANY).group(1, 2).anims(true, false, false).glow().fireImmune().light(8)
            .eggs(0x2A2323, 0xFF7A1A)),
    SCULK_MITE(p(EPIC, CRAWL).size(0.4f, 0.4f, 0.7f).health(5).speed(0.2f)
            .food(() -> Ingredient.of(Items.AMETHYST_SHARD)).product(() -> Items.EXPERIENCE_BOTTLE, 1)
            .habitat(Habitats::sculkMite, SpawnTime.ANY).group(1, 1).anims(true, false, false).extra("alert").glow().light(6)
            .eggs(0x0F2A33, 0x2EE6F0)),
    // ------------------------------------------------------------------ legendary
    GOLDEN_SCARAB(p(LEGENDARY, CRAWL).size(0.45f, 0.35f, 0.75f).health(6).speed(0.24f)
            .food(() -> Ingredient.of(Items.GOLDEN_CARROT)).product(() -> Items.GOLD_NUGGET, 2)
            .habitat(Habitats::goldenScarab, SpawnTime.NIGHT).group(1, 1).anims(true, true, false).eggs(0xF2C94C, 0x2F7FB5)),
    VOID_MOTH(p(LEGENDARY, FLY).size(0.5f, 0.35f, 0.75f).health(6).speed(0.2f).fly(0.4f)
            .food(() -> Ingredient.of(Items.CHORUS_FRUIT)).product(() -> Items.ENDER_PEARL, 1)
            .habitat(Habitats::voidMoth, SpawnTime.ANY).group(1, 1).anims(true, true, false).glow().light(9)
            .eggs(0x1C0F2E, 0xFF4FD8)),

    // ================================================================== expansion: common
    WORKER_ANT(p(COMMON, CRAWL).size(0.25f, 0.2f, 0.6f).health(1).speed(0.24f)
            .food(() -> Ingredient.of(Items.SUGAR)).product(ModItems.FRASS, 1)
            .habitat(MoreHabitats::workerAnt, SpawnTime.DAY).group(4, 8).anims(true, false, false).eggs(0x7A2A14, 0x2A120A)),
    EARWIG(p(COMMON, CRAWL).size(0.3f, 0.2f, 0.65f).health(2).speed(0.22f)
            .food(() -> Ingredient.of(Items.APPLE)).product(ModItems.FRASS, 1)
            .habitat(MoreHabitats::earwig, SpawnTime.NIGHT).group(1, 3).anims(true, false, false).action("pinch").eggs(0x3A2618, 0xC08A4A)),
    TERMITE(p(COMMON, CRAWL).size(0.25f, 0.2f, 0.55f).health(1).speed(0.18f)
            .food(() -> Ingredient.of(Items.STICK)).product(ModItems.FRASS, 1)
            .habitat(MoreHabitats::termite, SpawnTime.ANY).group(3, 6).anims(true, false, false).eggs(0xEFE2C4, 0xB5642A)),
    MILLIPEDE(p(COMMON, CRAWL).size(0.45f, 0.2f, 0.7f).health(4).speed(0.12f)
            .food(() -> Ingredient.of(Items.MOSS_BLOCK)).product(ModItems.FRASS, 1)
            .habitat(MoreHabitats::millipede, SpawnTime.NIGHT).group(1, 2).anims(true, false, false).extra("curl").eggs(0x151515, 0xD9531E)),
    CADDISFLY_LARVA(p(COMMON, AQUATIC).size(0.3f, 0.25f, 0.6f).health(2).speed(0.1f)
            .food(() -> Ingredient.of(Items.SEAGRASS)).product(() -> Items.CLAY_BALL, 1)
            .habitat(MoreHabitats::caddisflyLarva, SpawnTime.ANY).group(1, 3).anims(true, false, false).eggs(0x8A8174, 0x3B332A)),
    MOSQUITO(p(COMMON, FLY).size(0.3f, 0.25f, 0.6f).health(1).speed(0.2f).fly(0.45f)
            .food(() -> Ingredient.of(Items.SUGAR)).product(ModItems.FRASS, 1)
            .habitat(MoreHabitats::mosquito, SpawnTime.NIGHT).group(2, 4).anims(false, true, false).extra("fed").translucent()
            .eggs(0x2A2A2E, 0xB02020)),
    MAYFLY(p(COMMON, FLY).size(0.35f, 0.3f, 0.7f).health(1).speed(0.18f).fly(0.3f)
            .food(() -> Ingredient.of(Items.SEAGRASS)).product(ModItems.CRUNCHY_GRUB, 1)
            .habitat(MoreHabitats::mayfly, SpawnTime.ANY).group(3, 6).anims(false, true, false).translucent().eggs(0xF2E6A0, 0xD8D0C0)),
    GRASSHOPPER(p(COMMON, HOP).size(0.35f, 0.3f, 0.75f).health(2).speed(0.22f)
            .food(() -> Ingredient.of(Items.SHORT_GRASS)).product(ModItems.CRUNCHY_GRUB, 1)
            .habitat(MoreHabitats::grasshopper, SpawnTime.DAY).group(1, 3).anims(true, false, true).eggs(0x5DBB3A, 0xE3D04A)),
    SPRINGTAIL(p(COMMON, HOP).size(0.2f, 0.15f, 0.5f).health(1).speed(0.16f)
            .food(() -> Ingredient.of(Items.MOSS_CARPET)).product(ModItems.FRASS, 1)
            .habitat(MoreHabitats::springtail, SpawnTime.ANY).group(3, 6).anims(true, false, true).eggs(0x7C86A8, 0xB9A6D6)),
    WHIRLIGIG_BEETLE(p(COMMON, SKATE).size(0.3f, 0.2f, 0.6f).health(2).speed(0.28f)
            .food(() -> Ingredient.of(ModItems.CRUNCHY_GRUB.get())).product(ModItems.FRASS, 1)
            .habitat(MoreHabitats::whirligig, SpawnTime.DAY).group(2, 5).anims(true, false, false).eggs(0x141414, 0x8C6A2A)),
    STINK_BUG(p(COMMON, CRAWL).size(0.35f, 0.25f, 0.7f).health(3).speed(0.16f)
            .food(() -> Ingredient.of(Items.BEETROOT)).product(ModItems.FRASS, 1)
            .habitat(MoreHabitats::stinkBug, SpawnTime.ANY).group(1, 2).anims(true, false, false).action("spray").eggs(0x6E5E4A, 0x9C8A6A)),

    // ================================================================== expansion: uncommon
    ORB_WEAVER(p(UNCOMMON, CLIMB).size(0.4f, 0.3f, 0.75f).health(4).speed(0.2f)
            .food(() -> Ingredient.of(ModItems.CRUNCHY_GRUB.get())).product(ModItems.SILK, 1)
            .habitat(MoreHabitats::orbWeaver, SpawnTime.NIGHT).group(1, 1).anims(true, false, false).eggs(0xE8C21E, 0x1A1A1A)),
    TICK(p(UNCOMMON, CRAWL).size(0.2f, 0.15f, 0.5f).health(2).speed(0.18f)
            .food(() -> Ingredient.of(Items.BEEF)).product(ModItems.FRASS, 1)
            .habitat(MoreHabitats::tick, SpawnTime.DAY).group(1, 2).anims(true, false, false).eggs(0x7A2E1E, 0x2A1410)),
    CENTIPEDE(p(UNCOMMON, CRAWL).size(0.5f, 0.2f, 0.75f).health(8).speed(0.3f)
            .food(() -> Ingredient.of(Items.ROTTEN_FLESH)).product(ModItems.CHITIN, 1)
            .habitat(MoreHabitats::centipede, SpawnTime.ANY).group(1, 1).anims(true, false, false).eggs(0x8A3A1A, 0xE8A23A)),
    JUMPING_SPIDER(p(UNCOMMON, CRAWL).size(0.3f, 0.25f, 0.75f).health(3).speed(0.24f)
            .food(() -> Ingredient.of(ModItems.CRUNCHY_GRUB.get())).product(ModItems.SILK, 1)
            .habitat(MoreHabitats::jumpingSpider, SpawnTime.DAY).group(1, 1).anims(true, false, false).action("dance").eggs(0x151515, 0x2FC0B0)),
    HONEYPOT_ANT(p(UNCOMMON, CRAWL).size(0.35f, 0.3f, 0.7f).health(3).speed(0.14f)
            .food(() -> Ingredient.of(ModItems.HONEYDEW.get())).product(ModItems.HONEYDEW, 2)
            .habitat(MoreHabitats::honeypotAnt, SpawnTime.ANY).group(1, 2).anims(true, false, false).eggs(0xE8A42A, 0x2A160A)),
    ANTLION(p(UNCOMMON, CRAWL).size(0.35f, 0.2f, 0.7f).health(4).speed(0.12f)
            .food(() -> Ingredient.of(ModItems.CRUNCHY_GRUB.get())).product(ModItems.CHITIN, 1)
            .habitat(MoreHabitats::antlion, SpawnTime.ANY).group(1, 1).anims(true, false, false).action("grab").eggs(0xB8A882, 0x5A4A32)),
    BOOKWORM(p(UNCOMMON, CRAWL).size(0.2f, 0.15f, 0.55f).health(1).speed(0.12f)
            .food(() -> Ingredient.of(Items.PAPER)).product(() -> Items.PAPER, 2)
            .habitat(MoreHabitats::bookworm, SpawnTime.ANY).group(1, 2).anims(true, false, false).eggs(0xE8DCC0, 0x2A2420)),
    CICADA(p(UNCOMMON, CLIMB).size(0.35f, 0.3f, 0.8f).health(3).speed(0.16f)
            .food(() -> Ingredient.of(Items.ACACIA_LEAVES)).product(ModItems.CICADA_SHELL, 1)
            .habitat(MoreHabitats::cicada, SpawnTime.DAY).group(1, 2).anims(true, true, false).action("buzz").translucent()
            .eggs(0x2E3A22, 0xC8352A)),
    KATYDID(p(UNCOMMON, HOP).size(0.4f, 0.35f, 0.8f).health(3).speed(0.18f)
            .food(() -> Ingredient.of(Items.PUMPKIN_SEEDS)).product(ModItems.FRASS, 1)
            .habitat(MoreHabitats::katydid, SpawnTime.NIGHT).group(1, 2).anims(true, false, true).action("sing").eggs(0x5FA83A, 0x3F7A26)),
    HAWK_MOTH(p(UNCOMMON, FLY).size(0.4f, 0.3f, 0.75f).health(3).speed(0.2f).fly(0.55f)
            .food(() -> Ingredient.of(ItemTags.FLOWERS)).product(ModItems.HONEYDEW, 1)
            .habitat(MoreHabitats::hawkMoth, SpawnTime.DAY).group(1, 1).anims(false, true, false).eggs(0x6A6258, 0xE88A2A)),
    SAKURA_MOTH(p(UNCOMMON, FLY).size(0.4f, 0.3f, 0.75f).health(3).speed(0.18f).fly(0.3f)
            .food(() -> Ingredient.of(Items.PINK_PETALS)).product(() -> Items.PINK_PETALS, 2)
            .habitat(MoreHabitats::sakuraMoth, SpawnTime.ANY).group(1, 2).anims(false, true, false).eggs(0xF6C6D8, 0xE88AB0)),
    PAPER_WASP(p(UNCOMMON, FLY).size(0.35f, 0.3f, 0.7f).health(4).speed(0.22f).fly(0.45f)
            .food(() -> Ingredient.of(Items.SWEET_BERRIES)).product(() -> Items.PAPER, 1)
            .habitat(MoreHabitats::paperWasp, SpawnTime.DAY).group(2, 4).anims(true, true, false).translucent().eggs(0xE8C21E, 0x1E1A10)),
    LOCUST(p(UNCOMMON, FLY).size(0.35f, 0.3f, 0.7f).health(2).speed(0.2f).fly(0.4f)
            .food(() -> Ingredient.of(Items.WHEAT)).product(ModItems.CRUNCHY_GRUB, 1)
            .habitat(MoreHabitats::locust, SpawnTime.DAY).group(6, 12).anims(true, true, false).eggs(0xC8A24A, 0xD8505A)),
    PRAYING_MANTIS(p(UNCOMMON, CRAWL).size(0.35f, 0.5f, 0.8f).health(5).speed(0.16f)
            .food(() -> Ingredient.of(ModItems.CRUNCHY_GRUB.get())).product(ModItems.CHITIN, 1)
            .habitat(MoreHabitats::prayingMantis, SpawnTime.DAY).group(1, 1).anims(true, false, false).action("strike").eggs(0x6CC04A, 0x3A8A2A)),
    BOMBARDIER_BEETLE(p(UNCOMMON, CRAWL).size(0.3f, 0.25f, 0.75f).health(4).speed(0.2f)
            .food(() -> Ingredient.of(Items.SPIDER_EYE)).product(() -> Items.GUNPOWDER, 1)
            .habitat(MoreHabitats::bombardier, SpawnTime.NIGHT).group(1, 2).anims(true, false, false).action("spray").eggs(0xE8761E, 0x1A2A4A)),
    DIVING_BEETLE(p(UNCOMMON, SWIM).size(0.35f, 0.25f, 0.8f).health(4).speed(0.9f)
            .food(() -> Ingredient.of(Items.SALMON)).product(ModItems.CHITIN, 1)
            .habitat(MoreHabitats::divingBeetle, SpawnTime.ANY).group(1, 2).anims(true, false, false).eggs(0x2E3420, 0xD8C24A)),
    MOLE_CRICKET(p(UNCOMMON, CRAWL).size(0.35f, 0.25f, 0.75f).health(3).speed(0.16f)
            .food(() -> Ingredient.of(Items.POTATO)).product(ModItems.FRASS, 1).bonus(() -> Items.FLINT, 0.2f)
            .habitat(MoreHabitats::moleCricket, SpawnTime.NIGHT).group(1, 1).anims(true, false, false).action("dig").eggs(0x6A4A2E, 0x3A2818)),
    DARKLING_BEETLE(p(UNCOMMON, CRAWL).size(0.35f, 0.3f, 0.75f).health(4).speed(0.18f)
            .food(() -> Ingredient.of(Items.DEAD_BUSH)).productStack(BugSpecies::waterBottle)
            .habitat(MoreHabitats::darklingBeetle, SpawnTime.ANY).group(1, 2).anims(true, false, false).extra("bask").eggs(0x161616, 0x5A5A5A)),

    // ================================================================== expansion: rare
    SCORPION(p(RARE, CRAWL).size(0.45f, 0.3f, 0.8f).health(8).speed(0.2f)
            .food(() -> Ingredient.of(Items.SPIDER_EYE)).product(() -> Items.SPIDER_EYE, 1)
            .habitat(MoreHabitats::scorpion, SpawnTime.NIGHT).group(1, 1).anims(true, false, false).action("sting").glow().eggs(0xC89A4A, 0x6AF0E8)),
    TARANTULA(p(RARE, CRAWL).size(0.5f, 0.35f, 0.85f).health(10).speed(0.2f)
            .food(() -> Ingredient.of(ModItems.ROASTED_GRUB.get())).product(ModItems.SILK, 2)
            .habitat(MoreHabitats::tarantula, SpawnTime.NIGHT).group(1, 1).anims(true, false, false).eggs(0x241A14, 0xD8762A)),
    ICE_CRAWLER(p(RARE, CRAWL).size(0.35f, 0.2f, 0.7f).health(4).speed(0.18f)
            .food(() -> Ingredient.of(Items.SNOWBALL)).product(() -> Items.SNOWBALL, 2).bonus(() -> Items.BLUE_ICE, 0.05f)
            .habitat(MoreHabitats::iceCrawler, SpawnTime.ANY).group(1, 2).anims(true, false, false).translucent().eggs(0xBDE6F2, 0x6AA8C8)),
    GIANT_ISOPOD(p(RARE, AQUATIC).size(0.6f, 0.3f, 0.85f).health(10).speed(0.12f)
            .food(() -> Ingredient.of(Items.COD)).product(() -> Items.PRISMARINE_SHARD, 1).bonus(() -> Items.PRISMARINE_CRYSTALS, 0.3f)
            .habitat(MoreHabitats::giantIsopod, SpawnTime.ANY).group(1, 1).anims(true, false, false).extra("curl").eggs(0xB8A8C8, 0x3A2E48)),
    LUNA_MOTH(p(RARE, FLY).size(0.5f, 0.35f, 0.8f).health(4).speed(0.18f).fly(0.3f)
            .food(() -> Ingredient.of(Items.BIRCH_LEAVES)).product(ModItems.SILK, 2)
            .habitat(MoreHabitats::lunaMoth, SpawnTime.NIGHT).group(1, 1).anims(false, true, false).glow().light(7).eggs(0xB8F0C8, 0x8A5AA8)),
    MORPHO(p(RARE, FLY).size(0.45f, 0.3f, 0.8f).health(4).speed(0.2f).fly(0.35f)
            .food(() -> Ingredient.of(Items.SWEET_BERRIES)).product(() -> Items.LIGHT_BLUE_DYE, 2)
            .habitat(MoreHabitats::morpho, SpawnTime.DAY).group(1, 1).anims(false, true, false).glow().eggs(0x2A8AF0, 0x3A2A1A)),
    OWL_BUTTERFLY(p(RARE, FLY).size(0.5f, 0.3f, 0.85f).health(4).speed(0.18f).fly(0.3f)
            .food(() -> Ingredient.of(Items.APPLE)).product(ModItems.HONEYDEW, 1)
            .habitat(MoreHabitats::owlButterfly, SpawnTime.NIGHT).group(1, 1).anims(false, true, false).eggs(0x6A4A2A, 0xE8C21E)),
    LEAF_INSECT(p(RARE, CRAWL).size(0.45f, 0.3f, 0.8f).health(4).speed(0.12f)
            .food(() -> Ingredient.of(ItemTags.LEAVES)).product(() -> Items.JUNGLE_LEAVES, 2)
            .habitat(MoreHabitats::leafInsect, SpawnTime.ANY).group(1, 1).anims(true, false, false).eggs(0x6CB83A, 0x9AD86A)),
    CLICK_BEETLE(p(RARE, CRAWL).size(0.3f, 0.25f, 0.75f).health(3).speed(0.2f)
            .food(() -> Ingredient.of(Items.CARROT)).product(ModItems.GLOW_GOO, 1)
            .habitat(MoreHabitats::clickBeetle, SpawnTime.NIGHT).group(1, 1).anims(true, false, false).action("click").glow().light(6)
            .eggs(0x3A2A1E, 0x9AF04A)),
    SEA_SKATER(p(RARE, SKATE).size(0.4f, 0.15f, 0.7f).health(3).speed(0.3f)
            .food(() -> Ingredient.of(Items.DRIED_KELP)).product(() -> Items.KELP, 2)
            .habitat(MoreHabitats::seaSkater, SpawnTime.DAY).group(1, 3).anims(true, false, false).eggs(0xA8B0B8, 0x5A6470)),
    MUSHROOM_BEETLE(p(RARE, CRAWL).size(0.3f, 0.25f, 0.75f).health(3).speed(0.18f)
            .food(() -> Ingredient.of(Items.RED_MUSHROOM)).product(() -> Items.RED_MUSHROOM, 1).bonus(() -> Items.BROWN_MUSHROOM, 0.5f)
            .habitat(MoreHabitats::mushroomBeetle, SpawnTime.ANY).group(1, 2).anims(true, false, false).eggs(0xE8481E, 0x151515)),
    RAIN_BEETLE(p(RARE, CRAWL).size(0.35f, 0.3f, 0.75f).health(4).speed(0.2f)
            .food(() -> Ingredient.of(ItemTags.SAPLINGS)).product(ModItems.FRASS, 2)
            .habitat(MoreHabitats::rainBeetle, SpawnTime.ANY).group(1, 2).anims(true, false, false).eggs(0x7A4A22, 0xD8A84A)),

    // ================================================================== expansion: epic
    ATLAS_MOTH(p(EPIC, FLY).size(0.8f, 0.4f, 1.0f).health(10).speed(0.16f).fly(0.25f)
            .food(() -> Ingredient.EMPTY).product(ModItems.SILK, 3)
            .habitat(MoreHabitats::atlasMoth, SpawnTime.NIGHT).group(1, 1).anims(false, true, false).eggs(0x8A3A1E, 0xE8D86A)),
    SOUL_MOTH(p(EPIC, FLY).size(0.45f, 0.3f, 0.75f).health(6).speed(0.2f).fly(0.35f)
            .food(() -> Ingredient.of(Items.WARPED_FUNGUS)).product(() -> Items.SOUL_SAND, 1).bonus(() -> Items.GHAST_TEAR, 0.05f)
            .habitat(MoreHabitats::soulMoth, SpawnTime.ANY).group(1, 2).anims(false, true, false).glow().fireImmune().light(10)
            .eggs(0x3A2A1E, 0x4AE8F0)),
    GUST_MOTH(p(EPIC, FLY).size(0.45f, 0.3f, 0.75f).health(6).speed(0.22f).fly(0.45f)
            .food(() -> Ingredient.of(Items.WIND_CHARGE)).product(() -> Items.WIND_CHARGE, 2).bonus(() -> Items.BREEZE_ROD, 0.1f)
            .habitat(MoreHabitats::gustMoth, SpawnTime.ANY).group(1, 1).anims(false, true, false).action("gust").translucent()
            .eggs(0xBDE8E0, 0x6AC8C0)),
    SHULKER_MITE(p(EPIC, FLY).size(0.35f, 0.35f, 0.75f).health(8).speed(0.12f).fly(0.2f)
            .food(() -> Ingredient.of(Items.POPPED_CHORUS_FRUIT)).product(() -> Items.SHULKER_SHELL, 1)
            .habitat(MoreHabitats::shulkerMite, SpawnTime.ANY).group(1, 2).anims(false, true, false).glow().light(8).eggs(0x9A6AA8, 0xD8F04A)),
    CHORUS_WEEVIL(p(EPIC, CRAWL).size(0.35f, 0.3f, 0.75f).health(6).speed(0.16f)
            .food(() -> Ingredient.of(Items.CHORUS_FLOWER)).product(() -> Items.POPPED_CHORUS_FRUIT, 2)
            .habitat(MoreHabitats::chorusWeevil, SpawnTime.ANY).group(1, 2).anims(true, false, false).eggs(0xB88AD8, 0x5A3A7A)),
    ECHO_MOTH(p(EPIC, FLY).size(0.45f, 0.3f, 0.75f).health(6).speed(0.18f).fly(0.3f)
            .food(() -> Ingredient.of(Items.AMETHYST_SHARD)).product(() -> Items.SCULK_VEIN, 2).bonus(() -> Items.ECHO_SHARD, 0.08f)
            .habitat(MoreHabitats::echoMoth, SpawnTime.ANY).group(1, 1).anims(false, true, false).glow().light(5).eggs(0x0E2A30, 0x3AE8F0)),

    // ================================================================== expansion: legendary
    QUEEN_ANT(p(LEGENDARY, CRAWL).size(0.45f, 0.3f, 0.85f).health(10).speed(0.16f)
            .food(() -> Ingredient.of(ModItems.ROYAL_JELLY.get())).product(ModItems.ROYAL_JELLY, 1)
            .habitat(MoreHabitats::queenAnt, SpawnTime.DAY).group(1, 1).anims(true, false, false).eggs(0x6A1E0E, 0xE8C21E)),
    STORM_BEETLE(p(LEGENDARY, CRAWL).size(0.45f, 0.35f, 0.8f).health(10).speed(0.2f)
            .food(() -> Ingredient.of(Items.REDSTONE)).product(() -> Items.COPPER_INGOT, 2).bonus(() -> Items.LIGHTNING_ROD, 0.1f)
            .habitat(MoreHabitats::stormBeetle, SpawnTime.ANY).group(1, 1).anims(true, false, false).extra("charge").glow().fireImmune().light(9)
            .eggs(0x2A3038, 0xF0E83A)),
    CRYSTAL_BEETLE(p(LEGENDARY, CRAWL).size(0.45f, 0.35f, 0.8f).health(10).speed(0.18f)
            .food(() -> Ingredient.of(Items.QUARTZ)).product(() -> Items.AMETHYST_SHARD, 2).bonus(() -> Items.DIAMOND, 0.05f)
            .habitat(MoreHabitats::crystalBeetle, SpawnTime.ANY).group(1, 1).anims(true, false, false).glow().translucent().light(8)
            .eggs(0xB88AF0, 0x8AF0F0));

    private static ItemStack waterBottle() {
        return net.minecraft.world.item.alchemy.PotionContents.createItemStack(Items.POTION, net.minecraft.world.item.alchemy.Potions.WATER);
    }

    public static final Codec<BugSpecies> CODEC = StringRepresentable.fromEnum(BugSpecies::values);
    public static final StreamCodec<ByteBuf, BugSpecies> STREAM_CODEC =
            ByteBufCodecs.idMapper(i -> values()[i], Enum::ordinal);
    private static final Map<EntityType<?>, BugSpecies> BY_TYPE = new IdentityHashMap<>();

    private final String id;
    private final Props props;

    BugSpecies(Props props) {
        this.id = name().toLowerCase(Locale.ROOT);
        this.props = props;
    }

    public String id() { return id; }
    public BugRarity rarity() { return props.rarity; }
    public Movement movement() { return props.movement; }
    public float width() { return props.width; }
    public float height() { return props.height; }
    public float renderScale() { return props.renderScale; }
    public double health() { return props.health; }
    public double speed() { return props.speed; }
    public double flySpeed() { return props.flySpeed; }
    public Ingredient food() { return props.food.get(); }
    public int groupMin() { return props.groupMin; }
    public int groupMax() { return props.groupMax; }
    public Habitat habitat() { return props.habitat; }
    public SpawnTime spawnTime() { return props.time; }
    public boolean hasWalk() { return props.walk; }
    public boolean hasFly() { return props.fly; }
    public boolean hasHop() { return props.hop; }
    /** Animation triggered on the "action" controller (chirp, spar, horn), or null. */
    public String actionAnim() { return props.action; }
    /** Extra state animation (roll, alert), or null. */
    public String extraAnim() { return props.extra; }
    public boolean glows() { return props.glow; }
    public boolean translucent() { return props.translucent; }
    public boolean fireImmune() { return props.fireImmune; }
    /** Light a terrarium gives off while holding this bug. */
    public int terrariumLight() { return props.light; }
    public int eggPrimary() { return props.egg1; }
    public int eggSecondary() { return props.egg2; }
    public boolean flies() { return props.movement == FLY; }

    public ItemStack makeProduct() {
        if (props.productStack != null) {
            return props.productStack.get();
        }
        return new ItemStack(props.product.get(), props.productCount);
    }

    /** Bugs that cannot be fed (the atlas moth has no mouth) cannot breed either. */
    public boolean canEat() {
        return !food().isEmpty();
    }

    public ItemStack makeBonus(net.minecraft.util.RandomSource random) {
        if (props.bonus != null && random.nextFloat() < props.bonusChance) {
            return new ItemStack(props.bonus.get());
        }
        return ItemStack.EMPTY;
    }

    public Component displayName() {
        return Component.translatable(translationKey());
    }

    public String translationKey() {
        return "entity.bugslife." + id;
    }

    public String descriptionKey(String part) {
        return "bugslife.guide." + id + "." + part;
    }

    @Override
    public String getSerializedName() {
        return id;
    }

    public static void bindType(EntityType<?> type, BugSpecies species) {
        BY_TYPE.put(type, species);
    }

    public static BugSpecies byType(EntityType<?> type) {
        BugSpecies species = BY_TYPE.get(type);
        if (species == null) {
            throw new IllegalStateException("Not a bug entity type: " + type);
        }
        return species;
    }

    public static BugSpecies byId(String id) {
        for (BugSpecies s : values()) {
            if (s.id.equals(id)) {
                return s;
            }
        }
        return null;
    }

    // ------------------------------------------------------------------ builder

    private static Props p(BugRarity rarity, Movement movement) {
        return new Props(rarity, movement);
    }

    public enum SpawnTime { DAY, NIGHT, ANY }

    static final class Props {
        final BugRarity rarity;
        final Movement movement;
        float width = 0.3f, height = 0.3f, renderScale = 1f;
        double health = 2, speed = 0.2, flySpeed = 0.3;
        Supplier<Ingredient> food = () -> Ingredient.EMPTY;
        Supplier<? extends ItemLike> product = () -> Items.AIR;
        Supplier<ItemStack> productStack;
        int productCount = 1;
        Supplier<? extends ItemLike> bonus;
        float bonusChance;
        Habitat habitat = (level, origin, random) -> null;
        SpawnTime time = SpawnTime.ANY;
        int groupMin = 1, groupMax = 1;
        boolean walk, fly, hop, glow, translucent, fireImmune;
        String action, extra;
        int light;
        int egg1, egg2;

        Props(BugRarity rarity, Movement movement) {
            this.rarity = rarity;
            this.movement = movement;
        }

        Props size(float w, float h, float scale) { width = w; height = h; renderScale = scale; return this; }
        Props health(double v) { health = v; return this; }
        Props speed(double v) { speed = v; return this; }
        Props fly(double v) { flySpeed = v; return this; }
        Props food(Supplier<Ingredient> v) { food = v; return this; }
        Props product(Supplier<? extends ItemLike> v, int count) { product = v; productCount = count; return this; }
        Props productStack(Supplier<ItemStack> v) { productStack = v; return this; }
        Props bonus(Supplier<? extends ItemLike> v, float chance) { bonus = v; bonusChance = chance; return this; }
        Props habitat(Habitat h, SpawnTime t) { habitat = h; time = t; return this; }
        Props group(int min, int max) { groupMin = min; groupMax = max; return this; }
        Props anims(boolean walk, boolean fly, boolean hop) { this.walk = walk; this.fly = fly; this.hop = hop; return this; }
        Props action(String a) { action = a; return this; }
        Props extra(String a) { extra = a; return this; }
        Props glow() { glow = true; return this; }
        Props translucent() { translucent = true; return this; }
        Props fireImmune() { fireImmune = true; return this; }
        Props light(int l) { light = l; return this; }
        Props eggs(int a, int b) { egg1 = a; egg2 = b; return this; }
    }
}
