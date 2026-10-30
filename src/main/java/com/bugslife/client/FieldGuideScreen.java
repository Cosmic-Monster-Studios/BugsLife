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
 * The Field Guide: a catalog of all bugs (undiscovered ones are hidden but hint where to look) and a detail page
 * with a live, animated model of the selected bug.
 */
public class FieldGuideScreen extends Screen {
    private static final int MAX_W = 340;
    private static final int MAX_H = 214;
    private static final int COLS = 5;
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
    private double detailScroll;
    private int detailScrollMax;
    private boolean draggingDetail;
    private boolean initialized;

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
        if (selected != s) detailScroll = 0;
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

    private int bookWidth() {
        return Math.min(MAX_W, Math.max(1, width - 8));
    }

    private int bookHeight() {
        return Math.min(MAX_H, Math.max(1, height - 8));
    }

    private int tileSize() {
        int across = (bookWidth() / 2 - 16 - (COLS - 1) * 3) / COLS;
        int down = (navY() - 8 - gridY() - 3 * 5) / 4;
        return Math.max(16, Math.min(28, Math.min(across, down)));
    }

    private int gridX() {
        return left() + 8;
    }

    private int gridY() {
        return top() + 38;
    }

    private int tileX(int slot) {
        return gridX() + (slot % COLS) * (tileSize() + 3);
    }

    private int tileY(int slot) {
        return gridY() + (slot / COLS) * (tileSize() + 5);
    }

    private int prevX() {
        return gridX();
    }

    private int nextX() {
        return gridX() + COLS * tileSize() + (COLS - 1) * 3 - 12;
    }

    private int navY() {
        return top() + bookHeight() - 24;
    }

    private int detailX() {
        return left() + bookWidth() / 2 + 10;
    }

    private int detailTop() {
        return top() + 10;
    }

    private int detailBottom() {
        return top() + bookHeight() - 10;
    }

    private int detailWidth() {
        return Math.max(1, bookWidth() - bookWidth() / 2 - 28);
    }

    private int scrollX() {
        return left() + bookWidth() - 10;
    }

    private boolean overDetail(double mouseX, double mouseY) {
        return mouseX >= detailX() && mouseX < left() + bookWidth() - 4
                && mouseY >= detailTop() && mouseY < detailBottom();
    }

    @Override
    public void init() {
        super.init();
        if (!initialized) page = selected.ordinal() / PER_PAGE;
        page = Math.max(0, Math.min(pages() - 1, page));
        initialized = true;
    }

    @Override
    public void removed() {
        bookmark = selected;
        super.removed();
    }

    private int left() {
        return (width - bookWidth()) / 2;
    }

    private int top() {
        return (height - bookHeight()) / 2;
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }

    @Override
    public void renderBackground(GuiGraphics g, int mouseX, int mouseY, float partialTick) {
        super.renderBackground(g, mouseX, mouseY, partialTick);
        int x = left(), y = top();
        g.fill(x - 4, y - 4, x + bookWidth() + 4, y + bookHeight() + 4, LEATHER);
        g.fill(x, y, x + bookWidth(), y + bookHeight(), PAPER);
        g.fill(x + bookWidth() / 2 - 1, y + 4, x + bookWidth() / 2 + 1, y + bookHeight() - 4, PAPER_DARK);
    }

    @Override
    public void render(GuiGraphics g, int mouseX, int mouseY, float partialTick) {
        super.render(g, mouseX, mouseY, partialTick);
        BugJournal journal = ClientJournal.get();
        int x = left(), y = top();

        int catalogWidth = bookWidth() / 2 - 16;
        // Long translated headers remain available in their tooltip; the detail text scrolls in full.
        g.drawString(font, font.plainSubstrByWidth(title.getString(), catalogWidth), gridX(), y + 10, INK, false);
        Component progress = Component.translatable("gui.bugslife.discovered", journal.discovered(), BugSpecies.values().length);
        g.drawString(font, font.plainSubstrByWidth(progress.getString(), catalogWidth), gridX(), y + 22, INK_SOFT, false);
        int tile = tileSize();

        BugSpecies hovered = null;
        BugSpecies[] all = BugSpecies.values();
        int start = page * PER_PAGE;
        for (int i = start; i < Math.min(all.length, start + PER_PAGE); i++) {
            BugSpecies s = all[i];
            int slot = i - start;
            int tx = tileX(slot);
            int ty = tileY(slot);
            boolean known = journal.count(s) > 0;
            boolean hover = mouseX >= tx && mouseX < tx + tile && mouseY >= ty && mouseY < ty + tile;
            if (hover) hovered = s;
            if (s == selected) {
                g.fill(tx - 2, ty - 2, tx + tile + 2, ty + tile + 2, INK);
            }
            g.fill(tx, ty, tx + tile, ty + tile, hover ? 0xFFEADCB9 : PAPER_DARK);
            g.fill(tx, ty + tile - 2, tx + tile, ty + tile, 0xFF000000 | rarityColor(s));
            g.renderItem(BugJarItem.filled(new BugData(s, false, false)), tx + (tile - 16) / 2, ty + (tile - 16) / 2);
            if (!known) {
                // items render at a higher z than plain fills, so lift the cover above them
                g.pose().pushPose();
                g.pose().translate(0, 0, 250);
                g.fill(tx, ty, tx + tile, ty + tile - 2, 0xE6E3D3B0);
                g.drawString(font, "?", tx + tile / 2 - 2, ty + tile / 2 - 5, INK_SOFT, false);
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

        renderDetail(g, journal, partialTick);

        if (mouseX >= gridX() && mouseX < gridX() + catalogWidth && mouseY >= y + 8 && mouseY < y + 32) {
            g.renderTooltip(font, mouseY < y + 20 ? title : progress, mouseX, mouseY);
        } else if (hovered != null) {
            Component name = journal.count(hovered) > 0 ? hovered.displayName() : Component.literal("???");
            g.renderTooltip(font, name.copy().withStyle(hovered.rarity().color), mouseX, mouseY);
        }
    }

    private void renderDetail(GuiGraphics g, BugJournal journal, float partialTick) {
        int x = detailX(), y = detailTop(), pageW = detailWidth();
        int viewport = detailBottom() - y;
        int contentHeight = detailContents(null, journal, x, 0, pageW, partialTick);
        detailScrollMax = Math.max(0, contentHeight - viewport);
        detailScroll = Math.max(0, Math.min(detailScrollMax, detailScroll));
        g.enableScissor(x, y, x + pageW, detailBottom());
        try {
            detailContents(g, journal, x, y - (int) detailScroll, pageW, partialTick);
        } finally {
            g.disableScissor();
        }
        if (detailScrollMax > 0) {
            int sx = scrollX();
            int trackTop = y + 10, trackBottom = detailBottom() - 10;
            int trackHeight = Math.max(1, trackBottom - trackTop);
            int thumbHeight = Math.min(trackHeight, Math.max(14, trackHeight * viewport / contentHeight));
            int thumbY = trackTop + (int) ((trackHeight - thumbHeight) * detailScroll / detailScrollMax);
            g.fill(sx, trackTop, sx + 4, trackBottom, PAPER_DARK);
            g.fill(sx, thumbY, sx + 4, thumbY + thumbHeight, INK_SOFT);
            g.drawString(font, "^", sx - 1, y, detailScroll > 0 ? INK : PAPER_DARK, false);
            g.drawString(font, "v", sx - 1, detailBottom() - 8, detailScroll < detailScrollMax ? INK : PAPER_DARK, false);
        }
    }

    /** A shared measure/draw pass keeps the scroll limit aligned with wrapped translations and item rows. */
    private int detailContents(GuiGraphics g, BugJournal journal, int x, int y, int pageW, float partialTick) {
        int startY = y;
        BugSpecies s = selected;
        int caught = journal.count(s);
        boolean known = caught > 0;
        Component name = known ? s.displayName() : Component.literal("???");
        y = paragraph(g, null, name.copy().withStyle(ChatFormatting.BOLD), x, y, pageW, inkFor(s));
        y = paragraph(g, null, Component.translatable("bugslife.rarity." + s.rarity().getSerializedName()), x, y, pageW, inkFor(s));
        if (known) {
            y = paragraph(g, null, Component.translatable("gui.bugslife.caught", caught), x, y, pageW, INK_SOFT);
        }
        int modelY = y + 2;
        if (g != null) {
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
        }
        y = paragraph(g, Component.translatable("gui.bugslife.habitat").withStyle(ChatFormatting.DARK_GREEN),
                Component.translatable(s.descriptionKey("habitat")), x, modelY + 68, pageW, INK_SOFT);
        if (known) {
            ItemStack food = firstItem(s);
            if (!food.isEmpty()) {
                y = itemRow(g, Component.translatable("gui.bugslife.food"), food, x, y, pageW);
            }
            y = itemRow(g, Component.translatable("gui.bugslife.harvest"), s.makeProduct(), x, y, pageW);
            y = paragraph(g, null, Component.translatable(s.descriptionKey("fact")).withStyle(ChatFormatting.ITALIC),
                    x, y, pageW, INK_SOFT);
        } else {
            y = paragraph(g, null, Component.translatable("gui.bugslife.unknown").withStyle(ChatFormatting.ITALIC),
                    x, y + 2, pageW, INK_SOFT);
        }
        return y - startY;
    }

    private int itemRow(GuiGraphics g, Component label, ItemStack item, int x, int y, int w) {
        int labelEnd = paragraph(g, null, label, x, y + 4, Math.max(1, w - 22), INK);
        if (g != null) g.renderItem(item, x + w - 18, y);
        return Math.max(y + 19, labelEnd + 2);
    }

    private int paragraph(GuiGraphics g, Component heading, Component body, int x, int y, int w, int color) {
        if (heading != null) {
            for (FormattedCharSequence line : font.split(heading, w)) {
                if (g != null) g.drawString(font, line, x, y, INK, false);
                y += 10;
            }
        }
        List<FormattedCharSequence> lines = font.split(body, w);
        for (FormattedCharSequence line : lines) {
            if (g != null) g.drawString(font, line, x, y, color, false);
            y += 9;
        }
        return y + 3;
    }

    private void scrollToMouse(double mouseY) {
        double fraction = (mouseY - detailTop() - 10) / Math.max(1, detailBottom() - detailTop() - 20);
        detailScroll = Math.max(0, Math.min(detailScrollMax, fraction * detailScrollMax));
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
        int tile = tileSize();
        if (button == 0 && detailScrollMax > 0 && mouseX >= scrollX() - 3 && mouseX < scrollX() + 7
                && mouseY >= detailTop() && mouseY < detailBottom()) {
            draggingDetail = true;
            scrollToMouse(mouseY);
            return true;
        }
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
            int tx = tileX(slot);
            int ty = tileY(slot);
            if (mouseX >= tx && mouseX < tx + tile && mouseY >= ty && mouseY < ty + tile) {
                select(all[i]);
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
            case 268 -> {                                          // home: start of detail
                detailScroll = 0;
                return true;
            }
            case 269 -> {                                          // end: end of detail
                detailScroll = detailScrollMax;
                return true;
            }
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
        if (scrollY == 0) return super.mouseScrolled(mouseX, mouseY, scrollX, scrollY);
        if (overDetail(mouseX, mouseY)) {
            detailScroll = Math.max(0, Math.min(detailScrollMax, detailScroll - scrollY * 18));
            return true;
        }
        if (mouseX >= left() && mouseX < left() + bookWidth() / 2
                && mouseY >= top() && mouseY < top() + bookHeight()) {
            turnPage(scrollY > 0 ? -1 : 1);
            return true;
        }
        return super.mouseScrolled(mouseX, mouseY, scrollX, scrollY);
    }

    @Override
    public boolean mouseDragged(double mouseX, double mouseY, int button, double dragX, double dragY) {
        if (draggingDetail && button == 0) {
            scrollToMouse(mouseY);
            return true;
        }
        return super.mouseDragged(mouseX, mouseY, button, dragX, dragY);
    }

    @Override
    public boolean mouseReleased(double mouseX, double mouseY, int button) {
        if (draggingDetail && button == 0) {
            draggingDetail = false;
            return true;
        }
        return super.mouseReleased(mouseX, mouseY, button);
    }
}
