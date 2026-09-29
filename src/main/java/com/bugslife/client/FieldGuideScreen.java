package com.bugslife.client;

import com.bugslife.bug.BugData;
import com.bugslife.bug.BugJournal;
import com.bugslife.bug.BugSpecies;
import com.bugslife.entity.BugEntity;
import com.bugslife.item.BugJarItem;
import com.bugslife.network.ClientJournal;
import net.minecraft.ChatFormatting;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.screens.inventory.InventoryScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.world.item.ItemStack;
import org.joml.Quaternionf;
import org.joml.Vector3f;

import java.util.EnumMap;
import java.util.List;
import java.util.Map;

/**
 * The Field Guide: a page of all twenty bugs (undiscovered ones are hidden but hint where to look) and a detail page
 * with a live, animated model of the selected bug.
 */
public class FieldGuideScreen extends Screen {
    private static final int W = 340;
    private static final int H = 214;
    private static final int COLS = 5;
    private static final int TILE = 28;
    private static final int PER_PAGE = 20;

    private static final int PAPER = 0xFFF1E6CC;
    private static final int PAPER_DARK = 0xFFE3D3B0;
    private static final int INK = 0xFF3B2E22;
    private static final int INK_SOFT = 0xFF6E5B45;
    private static final int LEATHER = 0xFF5A3E26;

    private final Map<BugSpecies, BugEntity> previews = new EnumMap<>(BugSpecies.class);
    /** Remembered between openings, like a bookmark. */
    private static BugSpecies bookmark;
    private BugSpecies selected;
    private int page;

    public FieldGuideScreen() {
        super(Component.translatable("gui.bugslife.field_guide"));
        selected = bookmark;
        if (selected == null) {
            selected = BugSpecies.LADYBUG;
            for (BugSpecies s : BugSpecies.values()) {
                if (ClientJournal.get().count(s) > 0) {
                    selected = s;
                    break;
                }
            }
        }
    }

    private int pages() {
        return (BugSpecies.values().length + PER_PAGE - 1) / PER_PAGE;
    }

    private void select(BugSpecies s) {
        selected = s;
        page = s.ordinal() / PER_PAGE;
    }

    private void turnPage(int delta) {
        int next = Math.max(0, Math.min(pages() - 1, page + delta));
        if (next != page) {
            page = next;
            Minecraft.getInstance().getSoundManager().play(net.minecraft.client.resources.sounds.SimpleSoundInstance.forUI(
                    net.minecraft.sounds.SoundEvents.BOOK_PAGE_TURN, 1.0f));
        }
    }

    private int prevX() {
        return left() + 14;
    }

    private int nextX() {
        return left() + 14 + COLS * (TILE + 4) - 12;
    }

    private int navY() {
        return top() + 28 + 4 * (TILE + 5) + 4;
    }

    @Override
    public void init() {
        super.init();
        page = selected.ordinal() / PER_PAGE;
    }

    @Override
    public void removed() {
        bookmark = selected;
        super.removed();
    }

    private int left() {
        return (width - W) / 2;
    }

    private int top() {
        return (height - H) / 2;
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }

    @Override
    public void renderBackground(GuiGraphics g, int mouseX, int mouseY, float partialTick) {
        super.renderBackground(g, mouseX, mouseY, partialTick);
        int x = left(), y = top();
        g.fill(x - 4, y - 4, x + W + 4, y + H + 4, LEATHER);
        g.fill(x, y, x + W, y + H, PAPER);
        g.fill(x + W / 2 - 1, y + 4, x + W / 2 + 1, y + H - 4, PAPER_DARK);
    }

    @Override
    public void render(GuiGraphics g, int mouseX, int mouseY, float partialTick) {
        super.render(g, mouseX, mouseY, partialTick);
        BugJournal journal = ClientJournal.get();
        int x = left(), y = top();

        g.drawString(font, title, x + 12, y + 10, INK, false);
        Component progress = Component.translatable("gui.bugslife.discovered", journal.discovered(), BugSpecies.values().length);
        g.drawString(font, progress, x + W / 2 - 10 - font.width(progress), y + 10, INK_SOFT, false);

        BugSpecies hovered = null;
        BugSpecies[] all = BugSpecies.values();
        int start = page * PER_PAGE;
        for (int i = start; i < Math.min(all.length, start + PER_PAGE); i++) {
            BugSpecies s = all[i];
            int slot = i - start;
            int tx = x + 14 + (slot % COLS) * (TILE + 4);
            int ty = y + 28 + (slot / COLS) * (TILE + 5);
            boolean known = journal.count(s) > 0;
            boolean hover = mouseX >= tx && mouseX < tx + TILE && mouseY >= ty && mouseY < ty + TILE;
            if (hover) hovered = s;
            if (s == selected) {
                g.fill(tx - 2, ty - 2, tx + TILE + 2, ty + TILE + 2, INK);
            }
            g.fill(tx, ty, tx + TILE, ty + TILE, hover ? 0xFFEADCB9 : PAPER_DARK);
            g.fill(tx, ty + TILE - 2, tx + TILE, ty + TILE, 0xFF000000 | rarityColor(s));
            g.renderItem(BugJarItem.filled(new BugData(s, false, false)), tx + 6, ty + 5);
            if (!known) {
                // items render at a higher z than plain fills, so lift the cover above them
                g.pose().pushPose();
                g.pose().translate(0, 0, 250);
                g.fill(tx, ty, tx + TILE, ty + TILE - 2, 0xE6E3D3B0);
                g.drawString(font, "?", tx + TILE / 2 - 2, ty + TILE / 2 - 5, INK_SOFT, false);
                g.pose().popPose();
            }
        }

        // page navigation
        Component pageLabel = Component.translatable("gui.bugslife.page", page + 1, pages());
        int midX = prevX() + (nextX() + 12 - prevX()) / 2;
        g.drawString(font, pageLabel, midX - font.width(pageLabel) / 2, navY() + 2, INK_SOFT, false);
        if (page > 0) {
            boolean hot = mouseX >= prevX() && mouseX < prevX() + 12 && mouseY >= navY() && mouseY < navY() + 12;
            g.drawString(font, "<", prevX() + 3, navY() + 2, hot ? INK : INK_SOFT, false);
        }
        if (page < pages() - 1) {
            boolean hot = mouseX >= nextX() && mouseX < nextX() + 12 && mouseY >= navY() && mouseY < navY() + 12;
            g.drawString(font, ">", nextX() + 3, navY() + 2, hot ? INK : INK_SOFT, false);
        }

        renderDetail(g, journal, x + W / 2 + 10, y + 10, partialTick);

        if (hovered != null) {
            Component name = journal.count(hovered) > 0 ? hovered.displayName() : Component.literal("???");
            g.renderTooltip(font, name.copy().withStyle(hovered.rarity().color), mouseX, mouseY);
        }
    }

    private void renderDetail(GuiGraphics g, BugJournal journal, int x, int y, float partialTick) {
        BugSpecies s = selected;
        int pageW = W / 2 - 20;
        int caught = journal.count(s);
        boolean known = caught > 0;

        Component name = known ? s.displayName() : Component.literal("???");
        g.drawString(font, name.copy().withStyle(ChatFormatting.BOLD), x, y, inkFor(s), false);
        g.drawString(font, Component.translatable("bugslife.rarity." + s.rarity().getSerializedName()), x, y + 11, inkFor(s), false);
        if (known) {
            Component c = Component.translatable("gui.bugslife.caught", caught);
            g.drawString(font, c, x + pageW - font.width(c), y + 11, INK_SOFT, false);
        }

        int modelY = y + 24;
        g.fill(x, modelY, x + pageW, modelY + 62, PAPER_DARK);
        if (known) {
            renderModel(g, s, x + pageW / 2, modelY + 44, partialTick);
        } else {
            g.pose().pushPose();
            g.pose().translate(x + pageW / 2f - 6, modelY + 18, 0);
            g.pose().scale(3, 3, 1);
            g.drawString(font, "?", 0, 0, INK_SOFT, false);
            g.pose().popPose();
        }

        int ty = modelY + 68;
        ty = paragraph(g, Component.translatable("gui.bugslife.habitat").withStyle(ChatFormatting.DARK_GREEN),
                Component.translatable(s.descriptionKey("habitat")), x, ty, pageW);
        if (known) {
            ItemStack food = firstItem(s);
            if (!food.isEmpty()) {
                g.drawString(font, Component.translatable("gui.bugslife.food"), x, ty + 4, INK, false);
                g.renderItem(food, x + pageW - 18, ty);
                ty += 17;
            }
            ItemStack product = s.makeProduct();
            g.drawString(font, Component.translatable("gui.bugslife.harvest"), x, ty + 4, INK, false);
            g.renderItem(product, x + pageW - 18, ty);
            ty += 19;
            paragraph(g, null, Component.translatable(s.descriptionKey("fact")).withStyle(ChatFormatting.ITALIC), x, ty, pageW);
        } else {
            paragraph(g, null, Component.translatable("gui.bugslife.unknown").withStyle(ChatFormatting.ITALIC), x, ty + 2, pageW);
        }
    }

    private int paragraph(GuiGraphics g, Component heading, Component body, int x, int y, int w) {
        if (heading != null) {
            g.drawString(font, heading, x, y, INK, false);
            y += 10;
        }
        List<FormattedCharSequence> lines = font.split(body, w);
        for (FormattedCharSequence line : lines) {
            g.drawString(font, line, x, y, INK_SOFT, false);
            y += 9;
        }
        return y + 3;
    }

    private void renderModel(GuiGraphics g, BugSpecies s, int cx, int cy, float partialTick) {
        Minecraft mc = Minecraft.getInstance();
        if (mc.level == null || mc.player == null) return;
        BugEntity bug = previews.computeIfAbsent(s, sp -> BugEntity.fromData(mc.level, new BugData(sp, false, false)));
        if (bug == null) return;
        bug.tickCount = mc.player.tickCount;
        bug.setOnGround(!s.flies());
        float spin = (mc.player.tickCount + partialTick) * 1.5f;
        bug.yBodyRot = bug.yBodyRotO = 0;
        bug.yHeadRot = bug.yHeadRotO = 0;
        bug.setYRot(0);
        float size = Math.max(s.width() * s.renderScale() * 1.6f, s.height() * 0.9f);
        float scale = Math.min(90f, 34f / size);
        Quaternionf pose = new Quaternionf().rotateZ((float) Math.PI).rotateX(-0.45f).rotateY((float) Math.toRadians(spin));
        float lift = s == BugSpecies.GLOWWORM ? -0.1f : 0f;
        InventoryScreen.renderEntityInInventory(g, cx, cy, scale, new Vector3f(0, lift, 0), pose, null, bug);
    }

    private static ItemStack firstItem(BugSpecies s) {
        ItemStack[] items = s.food().getItems();
        return items.length > 0 ? items[0] : ItemStack.EMPTY;
    }

    /** Rarity colours dark enough to read on parchment. */
    private static int inkFor(BugSpecies s) {
        return switch (s.rarity()) {
            case COMMON -> 0xFF5A4A3A;
            case UNCOMMON -> 0xFF2E7D32;
            case RARE -> 0xFF1C7FA0;
            case EPIC -> 0xFF8E24AA;
            case LEGENDARY -> 0xFFC06F00;
        };
    }

    private static int rarityColor(BugSpecies s) {
        Integer c = s.rarity().color.getColor();
        return c == null ? 0xFFFFFF : c;
    }

    @Override
    public boolean mouseClicked(double mouseX, double mouseY, int button) {
        int x = left(), y = top();
        if (mouseY >= navY() && mouseY < navY() + 12) {
            if (mouseX >= prevX() && mouseX < prevX() + 12) {
                turnPage(-1);
                return true;
            }
            if (mouseX >= nextX() && mouseX < nextX() + 12) {
                turnPage(1);
                return true;
            }
        }
        BugSpecies[] all = BugSpecies.values();
        int start = page * PER_PAGE;
        for (int i = start; i < Math.min(all.length, start + PER_PAGE); i++) {
            int slot = i - start;
            int tx = x + 14 + (slot % COLS) * (TILE + 4);
            int ty = y + 28 + (slot / COLS) * (TILE + 5);
            if (mouseX >= tx && mouseX < tx + TILE && mouseY >= ty && mouseY < ty + TILE) {
                selected = all[i];
                Minecraft.getInstance().getSoundManager().play(net.minecraft.client.resources.sounds.SimpleSoundInstance.forUI(
                        net.minecraft.sounds.SoundEvents.BOOK_PAGE_TURN, 1.0f));
                return true;
            }
        }
        return super.mouseClicked(mouseX, mouseY, button);
    }

    @Override
    public boolean keyPressed(int keyCode, int scanCode, int modifiers) {
        BugSpecies[] all = BugSpecies.values();
        int i = selected.ordinal();
        switch (keyCode) {
            case 262 -> i = Math.min(all.length - 1, i + 1);      // right
            case 263 -> i = Math.max(0, i - 1);                    // left
            case 264 -> i = Math.min(all.length - 1, i + COLS);   // down
            case 265 -> i = Math.max(0, i - COLS);                 // up
            case 266 -> {                                          // page up
                turnPage(-1);
                return true;
            }
            case 267 -> {                                          // page down
                turnPage(1);
                return true;
            }
            default -> {
                return super.keyPressed(keyCode, scanCode, modifiers);
            }
        }
        select(all[i]);
        return true;
    }

    @Override
    public boolean mouseScrolled(double mouseX, double mouseY, double scrollX, double scrollY) {
        turnPage(scrollY > 0 ? -1 : 1);
        return true;
    }
}
