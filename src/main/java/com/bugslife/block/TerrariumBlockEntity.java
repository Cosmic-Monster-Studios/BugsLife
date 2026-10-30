package com.bugslife.block;

import com.bugslife.Config;
import com.bugslife.bug.BugData;
import com.bugslife.bug.BugSpecies;
import com.bugslife.bug.Movement;
import com.bugslife.entity.BugEntity;
import com.bugslife.item.BugJarItem;
import com.bugslife.registry.ModBlockEntities;
import com.bugslife.registry.ModItems;
import com.bugslife.registry.ModTriggers;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.component.DataComponents;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.NbtOps;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.ComponentSerialization;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.network.protocol.Packet;
import net.minecraft.network.protocol.game.ClientGamePacketListener;
import net.minecraft.network.protocol.game.ClientboundBlockEntityDataPacket;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.StringUtil;
import net.minecraft.world.Containers;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.ItemInteractionResult;
import net.minecraft.world.entity.MobSpawnType;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.neoforged.neoforge.items.IItemHandler;
import net.neoforged.neoforge.items.ItemHandlerHelper;
import net.neoforged.neoforge.items.ItemStackHandler;
import org.jetbrains.annotations.Nullable;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

public class TerrariumBlockEntity extends BlockEntity {
    private static final int BREED_TICKS = 1200;

    /** One resident bug: what it is, its name tag (if any) and ticks until its next harvest. */
    public static final class Resident {
        public final BugData data;
        @Nullable final Component name;
        int timer;

        Resident(BugData data, @Nullable Component name, int timer) {
            this.data = data;
            this.name = name;
            this.timer = timer;
        }
    }

    private final List<Resident> residents = new ArrayList<>();
    private final ItemStackHandler output = new ItemStackHandler(9) {
        @Override
        protected void onContentsChanged(int slot) {
            setChanged();
        }
    };
    private final IItemHandler extractOnly = new IItemHandler() {
        @Override public int getSlots() { return output.getSlots(); }
        @Override public ItemStack getStackInSlot(int slot) { return output.getStackInSlot(slot); }
        @Override public ItemStack insertItem(int slot, ItemStack stack, boolean simulate) { return stack; }
        @Override public ItemStack extractItem(int slot, int amount, boolean simulate) { return output.extractItem(slot, amount, simulate); }
        @Override public int getSlotLimit(int slot) { return output.getSlotLimit(slot); }
        @Override public boolean isItemValid(int slot, ItemStack stack) { return false; }
    };
    private int breedTimer;
    private BugSpecies breeding;
    private UUID breeder;

    /** Client-side render cache of bug entities; see TerrariumRenderer. */
    public List<BugEntity> renderBugs;
    public int renderVersion;

    public TerrariumBlockEntity(BlockPos pos, BlockState state) {
        super(ModBlockEntities.TERRARIUM.get(), pos, state);
    }

    public IItemHandler getOutputHandler() {
        return extractOnly;
    }

    public List<BugData> bugs() {
        List<BugData> list = new ArrayList<>();
        for (Resident r : residents) list.add(r.data);
        return list;
    }

    public int capacity() {
        return getBlockState().getBlock() instanceof TerrariumBlock t ? t.capacity : 4;
    }

    private float speed() {
        return getBlockState().getBlock() instanceof TerrariumBlock t ? t.speed : 1.0f;
    }

    public int bugCount() {
        return residents.size();
    }

    public boolean isBreeding() {
        return breedTimer > 0;
    }

    private int produceTime(BugSpecies species) {
        int base = species.rarity().produceTicks;
        return (int) (base * (0.8 + level.random.nextDouble() * 0.4) / Config.TERRARIUM_SPEED.get() / speed());
    }

    // ------------------------------------------------------------------ ticking

    public static void serverTick(Level level, BlockPos pos, BlockState state, TerrariumBlockEntity be) {
        boolean changed = false;
        // countdowns that moved without anything else changing still need saving
        boolean ticked = false;
        // a queen ant sets her workers to double time; ice crawlers only thrive with ice beside the terrarium
        boolean queen = false;
        boolean crawler = false;
        for (Resident r : be.residents) {
            if (r.data.species() == BugSpecies.QUEEN_ANT) queen = true;
            if (r.data.species() == BugSpecies.ICE_CRAWLER) crawler = true;
        }
        boolean cold = crawler && be.isCold();
        for (Resident r : be.residents) {
            BugSpecies species = r.data.species();
            if (species == BugSpecies.ICE_CRAWLER && !cold) continue;
            if (r.timer > 0) {
                r.timer -= queen && species == BugSpecies.WORKER_ANT ? 2 : 1;
                ticked = true;
            }
            if (r.timer <= 0) {
                ItemStack product = species.makeProduct();
                // with no room for the harvest the bug waits, ready, until the output is emptied
                if (!ItemHandlerHelper.insertItemStacked(be.output, product, true).isEmpty()) {
                    r.timer = 0;
                    continue;
                }
                r.timer = be.produceTime(species);
                be.deposit(product);
                be.deposit(species.makeBonus(level.random));
                if (level instanceof ServerLevel sl) {
                    sl.sendParticles(ParticleTypes.HAPPY_VILLAGER, pos.getX() + 0.5, pos.getY() + 0.6, pos.getZ() + 0.5, 3, 0.25, 0.2, 0.25, 0);
                }
                changed = true;
            }
        }
        if (be.breedTimer > 0) {
            be.breedTimer--;
            ticked = true;
            if (be.breedTimer % 30 == 0 && level instanceof ServerLevel sl) {
                sl.sendParticles(ParticleTypes.HEART, pos.getX() + 0.5, pos.getY() + 0.7, pos.getZ() + 0.5, 1, 0.2, 0.1, 0.2, 0);
            }
            if (be.breedTimer == 0) {
                be.hatch();
                changed = true;
            }
        }
        if (changed) {
            be.setChanged();
        } else if (ticked) {
            // only mark the chunk unsaved: setChanged would update comparator neighbours every tick
            level.blockEntityChanged(pos);
        }
    }

    /** Ice or snow on any of the six sides. */
    private boolean isCold() {
        for (net.minecraft.core.Direction d : net.minecraft.core.Direction.values()) {
            BlockState next = level.getBlockState(worldPosition.relative(d));
            if (next.is(net.minecraft.tags.BlockTags.ICE) || next.is(net.minecraft.world.level.block.Blocks.SNOW_BLOCK)) return true;
        }
        return false;
    }

    private long countOf(BugSpecies s) {
        return residents.stream().filter(r -> r.data.species() == s).count();
    }

    private void deposit(ItemStack stack) {
        if (!stack.isEmpty()) {
            ItemStack rest = ItemHandlerHelper.insertItemStacked(output, stack, false);
            if (!rest.isEmpty()) Block.popResource(level, worldPosition.above(), rest);
        }
    }

    private void hatch() {
        // the pair must still be here (one may have been taken out mid-courtship)
        if (breeding == null || countOf(breeding) < 2 || residents.size() >= capacity()) {
            breeding = null;
            breeder = null;
            return;
        }
        boolean parentPrismatic = residents.stream().anyMatch(r -> r.data.species() == breeding && r.data.prismatic());
        boolean prismatic = level.random.nextInt(parentPrismatic ? 4 : 48) == 0;
        residents.add(new Resident(new BugData(breeding, prismatic, false), null, produceTime(breeding)));
        level.playSound(null, worldPosition, SoundEvents.CHICKEN_EGG, SoundSource.BLOCKS, 0.6f, 1.8f);
        if (level instanceof ServerLevel sl) {
            sl.sendParticles(ParticleTypes.HAPPY_VILLAGER, worldPosition.getX() + 0.5, worldPosition.getY() + 0.5, worldPosition.getZ() + 0.5, 8, 0.3, 0.3, 0.3, 0);
            if (breeder != null && sl.getPlayerByUUID(breeder) instanceof ServerPlayer sp) {
                ModTriggers.BUG_ACTION.get().trigger(sp, "terrarium_hatch");
                if (prismatic) {
                    sp.displayClientMessage(Component.translatable("bugslife.msg.prismatic_hatch", breeding.displayName())
                            .withStyle(ChatFormatting.LIGHT_PURPLE), false);
                }
            }
        }
        breeding = null;
        breeder = null;
        sync();
    }

    // ------------------------------------------------------------------ interaction

    public ItemInteractionResult useItem(ItemStack stack, Player player, InteractionHand hand) {
        if (stack.is(ModItems.BUG_JAR.get())) {
            BugData data = BugJarItem.getBug(stack);
            if (level.isClientSide) return ItemInteractionResult.SUCCESS;
            if (data != null) {
                if (residents.size() >= capacity()) {
                    player.displayClientMessage(Component.translatable("bugslife.msg.terrarium_full", capacity()).withStyle(ChatFormatting.YELLOW), true);
                    return ItemInteractionResult.CONSUME;
                }
                residents.add(new Resident(data, stack.get(DataComponents.CUSTOM_NAME), produceTime(data.species())));
                if (!player.getAbilities().instabuild) {
                    player.setItemInHand(hand, new ItemStack(ModItems.BUG_JAR.get()));
                }
                level.playSound(null, worldPosition, SoundEvents.BOTTLE_EMPTY, SoundSource.BLOCKS, 0.8f, 1.2f);
                if (player instanceof ServerPlayer sp) ModTriggers.BUG_ACTION.get().trigger(sp, "terrarium_insert");
                sync();
                return ItemInteractionResult.CONSUME;
            }
            if (residents.isEmpty()) {
                player.displayClientMessage(Component.translatable("bugslife.msg.terrarium_empty").withStyle(ChatFormatting.GRAY), true);
                return ItemInteractionResult.CONSUME;
            }
            Resident taken = residents.remove(residents.size() - 1);
            // a courtship needs both of the pair to stay
            if (breeding != null && countOf(breeding) < 2) {
                breeding = null;
                breeder = null;
                breedTimer = 0;
            }
            ItemStack filled = BugJarItem.filled(taken.data);
            if (taken.name != null) filled.set(DataComponents.CUSTOM_NAME, taken.name);
            stack.shrink(1);
            if (stack.isEmpty()) {
                player.setItemInHand(hand, filled);
            } else {
                // Inventory.add claims success for a creative player even when nothing fit
                boolean stored = (!player.getAbilities().instabuild || player.getInventory().getFreeSlot() >= 0)
                        && player.getInventory().add(filled);
                if (!stored) player.drop(filled, false);
            }
            level.playSound(null, worldPosition, SoundEvents.BOTTLE_FILL, SoundSource.BLOCKS, 0.8f, 1.2f);
            sync();
            return ItemInteractionResult.CONSUME;
        }

        // feeding a pair starts courtship
        BugSpecies pair = null;
        boolean anyEats = false;
        for (Resident r : residents) {
            if (r.data.species().canEat() && r.data.species().food().test(stack)) {
                anyEats = true;
                if (countOf(r.data.species()) >= 2) {
                    pair = r.data.species();
                    break;
                }
            }
        }
        if (!anyEats) return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
        if (level.isClientSide) return ItemInteractionResult.SUCCESS;
        if (pair == null) {
            player.displayClientMessage(Component.translatable("bugslife.msg.need_pair"), true);
            return ItemInteractionResult.CONSUME;
        }
        if (breedTimer > 0) {
            player.displayClientMessage(Component.translatable("bugslife.msg.already_breeding"), true);
            return ItemInteractionResult.CONSUME;
        }
        if (residents.size() >= capacity()) {
            player.displayClientMessage(Component.translatable("bugslife.msg.no_room").withStyle(ChatFormatting.YELLOW), true);
            return ItemInteractionResult.CONSUME;
        }
        if (!player.getAbilities().instabuild) stack.shrink(1);
        breeding = pair;
        breeder = player.getUUID();
        breedTimer = BREED_TICKS;
        level.playSound(null, worldPosition, SoundEvents.GENERIC_EAT, SoundSource.BLOCKS, 0.5f, 1.8f);
        ((ServerLevel) level).sendParticles(ParticleTypes.HEART, worldPosition.getX() + 0.5, worldPosition.getY() + 0.7,
                worldPosition.getZ() + 0.5, 4, 0.25, 0.1, 0.25, 0);
        if (player instanceof ServerPlayer sp) ModTriggers.BUG_ACTION.get().trigger(sp, "terrarium_breed");
        sync();
        return ItemInteractionResult.CONSUME;
    }

    public InteractionResult collect(Player player) {
        if (level.isClientSide) return InteractionResult.SUCCESS;
        boolean any = false;
        for (int i = 0; i < output.getSlots(); i++) {
            ItemStack s = output.extractItem(i, 64, false);
            if (!s.isEmpty()) {
                any = true;
                // Fill matching stacks and free slots before dropping any remainder.
                // Inventory.add alone silently deletes overflow for creative players.
                player.getInventory().placeItemBackInInventory(s);
            }
        }
        if (any) {
            level.playSound(null, worldPosition, SoundEvents.ITEM_PICKUP, SoundSource.BLOCKS, 0.5f, 1.2f);
            if (player instanceof ServerPlayer sp) ModTriggers.BUG_ACTION.get().trigger(sp, "terrarium_harvest");
            return InteractionResult.CONSUME;
        }
        player.displayClientMessage(status(), true);
        return InteractionResult.CONSUME;
    }

    private Component status() {
        if (residents.isEmpty()) {
            return Component.translatable("bugslife.msg.terrarium_empty").withStyle(ChatFormatting.GRAY);
        }
        // mirror serverTick: a queen doubles her workers' pace, and crawlers pause without the cold
        boolean queen = false;
        boolean crawler = false;
        for (Resident r : residents) {
            if (r.data.species() == BugSpecies.QUEEN_ANT) queen = true;
            if (r.data.species() == BugSpecies.ICE_CRAWLER) crawler = true;
        }
        boolean cold = crawler && isCold();
        MutableComponent line = Component.empty();
        int soonest = Integer.MAX_VALUE;
        for (int i = 0; i < residents.size(); i++) {
            Resident r = residents.get(i);
            BugSpecies species = r.data.species();
            if (i > 0) line.append(", ");
            line.append(species.displayName().copy().withStyle(species.rarity().color));
            if (species == BugSpecies.ICE_CRAWLER && !cold) continue;
            int eta = queen && species == BugSpecies.WORKER_ANT ? (r.timer + 1) / 2 : r.timer;
            soonest = Math.min(soonest, eta);
        }
        line.append(Component.literal(" - ").withStyle(ChatFormatting.GRAY));
        if (breedTimer > 0) {
            line.append(Component.translatable("bugslife.msg.courting", StringUtil.formatTickDuration(breedTimer, 20f)).withStyle(ChatFormatting.LIGHT_PURPLE));
        } else if (soonest == Integer.MAX_VALUE) {
            // every resident is an ice crawler waiting for the cold
            line.append(Component.translatable("bugslife.msg.needs_cold").withStyle(ChatFormatting.YELLOW));
        } else {
            line.append(Component.translatable("bugslife.msg.next_harvest", StringUtil.formatTickDuration(soonest, 20f)).withStyle(ChatFormatting.GRAY));
        }
        return line;
    }

    /** Breaking the terrarium lets the bugs out and drops the harvest. */
    public void releaseAll() {
        if (!(level instanceof ServerLevel server)) return;
        for (Resident r : residents) {
            BugEntity bug = BugEntity.fromData(server, r.data);
            if (bug != null) {
                bug.moveTo(worldPosition.getX() + 0.5, worldPosition.getY() + 0.1, worldPosition.getZ() + 0.5, level.random.nextFloat() * 360f, 0);
                bug.finalizeSpawn(server, server.getCurrentDifficultyAt(worldPosition), MobSpawnType.BUCKET, null);
                bug.setPrismatic(r.data.prismatic());
                if (r.name != null) bug.setCustomName(r.name);
                if (r.data.species().movement() == Movement.HANG) bug.attachToCeiling();
                if (server.addFreshEntity(bug)) continue;
            }
            // a bug that can't be let out stays in a jar rather than vanishing
            ItemStack jar = BugJarItem.filled(r.data);
            if (r.name != null) jar.set(DataComponents.CUSTOM_NAME, r.name);
            Containers.dropItemStack(level, worldPosition.getX() + 0.5, worldPosition.getY() + 0.5, worldPosition.getZ() + 0.5, jar);
        }
        residents.clear();
        for (int i = 0; i < output.getSlots(); i++) {
            Containers.dropItemStack(level, worldPosition.getX() + 0.5, worldPosition.getY() + 0.5, worldPosition.getZ() + 0.5, output.getStackInSlot(i));
            output.setStackInSlot(i, ItemStack.EMPTY);
        }
    }

    private void sync() {
        setChanged();
        if (level != null && !level.isClientSide) {
            int light = 0;
            for (Resident r : residents) light = Math.max(light, r.data.species().terrariumLight());
            BlockState state = getBlockState();
            if (state.getValue(TerrariumBlock.LIGHT) != light) {
                level.setBlock(worldPosition, state.setValue(TerrariumBlock.LIGHT, light), Block.UPDATE_ALL);
            }
            level.sendBlockUpdated(worldPosition, getBlockState(), getBlockState(), Block.UPDATE_CLIENTS);
        }
    }

    // ------------------------------------------------------------------ saving & syncing

    private void writeBugs(CompoundTag tag, HolderLookup.Provider registries) {
        ListTag list = new ListTag();
        for (Resident r : residents) {
            CompoundTag t = new CompoundTag();
            BugData.CODEC.encodeStart(NbtOps.INSTANCE, r.data).result().ifPresent(d -> t.put("Bug", d));
            t.putInt("Timer", r.timer);
            if (r.name != null) {
                ComponentSerialization.CODEC.encodeStart(registries.createSerializationContext(NbtOps.INSTANCE), r.name)
                        .result().ifPresent(n -> t.put("Name", n));
            }
            list.add(t);
        }
        tag.put("Bugs", list);
        tag.putInt("BreedTimer", breedTimer);
        if (breeding != null) tag.putString("Breeding", breeding.id());
    }

    private void readBugs(CompoundTag tag, HolderLookup.Provider registries) {
        residents.clear();
        ListTag list = tag.getList("Bugs", Tag.TAG_COMPOUND);
        for (int i = 0; i < list.size(); i++) {
            CompoundTag t = list.getCompound(i);
            Component name = t.contains("Name")
                    ? ComponentSerialization.CODEC.parse(registries.createSerializationContext(NbtOps.INSTANCE), t.get("Name")).result().orElse(null)
                    : null;
            BugData.CODEC.parse(NbtOps.INSTANCE, t.get("Bug")).result()
                    .ifPresent(d -> residents.add(new Resident(d, name, t.getInt("Timer"))));
        }
        breedTimer = tag.getInt("BreedTimer");
        breeding = tag.contains("Breeding") ? BugSpecies.byId(tag.getString("Breeding")) : null;
        renderVersion++;
    }

    @Override
    protected void saveAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.saveAdditional(tag, registries);
        writeBugs(tag, registries);
        tag.put("Output", output.serializeNBT(registries));
        if (breeder != null) tag.putUUID("Breeder", breeder);
    }

    @Override
    protected void loadAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.loadAdditional(tag, registries);
        readBugs(tag, registries);
        if (tag.contains("Output")) output.deserializeNBT(registries, tag.getCompound("Output"));
        breeder = tag.hasUUID("Breeder") ? tag.getUUID("Breeder") : null;
    }

    @Override
    public CompoundTag getUpdateTag(HolderLookup.Provider registries) {
        CompoundTag tag = new CompoundTag();
        writeBugs(tag, registries);
        return tag;
    }

    @Override
    public Packet<ClientGamePacketListener> getUpdatePacket() {
        return ClientboundBlockEntityDataPacket.create(this);
    }
}
