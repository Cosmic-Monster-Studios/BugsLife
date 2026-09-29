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
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.NbtOps;
import net.minecraft.nbt.Tag;
import net.minecraft.network.chat.Component;
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

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

public class TerrariumBlockEntity extends BlockEntity {
    private static final int BREED_TICKS = 1200;

    /** One resident bug: what it is and ticks until its next harvest. */
    public static final class Resident {
        public final BugData data;
        int timer;

        Resident(BugData data, int timer) {
            this.data = data;
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
        // a queen ant sets her workers to double time; ice crawlers only thrive with ice beside the terrarium
        boolean queen = false;
        for (Resident r : be.residents) {
            if (r.data.species() == BugSpecies.QUEEN_ANT) queen = true;
        }
        boolean cold = false;
        for (net.minecraft.core.Direction d : net.minecraft.core.Direction.values()) {
            BlockState next = level.getBlockState(pos.relative(d));
            if (next.is(net.minecraft.tags.BlockTags.ICE) || next.is(net.minecraft.world.level.block.Blocks.SNOW_BLOCK)) cold = true;
        }
        for (Resident r : be.residents) {
            BugSpecies species = r.data.species();
            if (species == BugSpecies.ICE_CRAWLER && !cold) continue;
            r.timer -= queen && species == BugSpecies.WORKER_ANT ? 2 : 1;
            if (r.timer <= 0) {
                r.timer = be.produceTime(r.data.species());
                be.deposit(r.data.species().makeProduct());
                be.deposit(r.data.species().makeBonus(level.random));
                if (level instanceof ServerLevel sl) {
                    sl.sendParticles(ParticleTypes.HAPPY_VILLAGER, pos.getX() + 0.5, pos.getY() + 0.6, pos.getZ() + 0.5, 3, 0.25, 0.2, 0.25, 0);
                }
                changed = true;
            }
        }
        if (be.breedTimer > 0) {
            be.breedTimer--;
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
        }
    }

    private void deposit(ItemStack stack) {
        if (!stack.isEmpty()) {
            ItemHandlerHelper.insertItemStacked(output, stack, false);
        }
    }

    private void hatch() {
        if (breeding == null || residents.size() >= capacity()) {
            breeding = null;
            return;
        }
        boolean parentPrismatic = residents.stream().anyMatch(r -> r.data.species() == breeding && r.data.prismatic());
        boolean prismatic = level.random.nextInt(parentPrismatic ? 4 : 48) == 0;
        residents.add(new Resident(new BugData(breeding, prismatic, false), produceTime(breeding)));
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
                residents.add(new Resident(data, produceTime(data.species())));
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
            ItemStack filled = BugJarItem.filled(taken.data);
            stack.shrink(1);
            if (stack.isEmpty()) {
                player.setItemInHand(hand, filled);
            } else if (!player.getInventory().add(filled)) {
                player.drop(filled, false);
            }
            level.playSound(null, worldPosition, SoundEvents.BOTTLE_FILL, SoundSource.BLOCKS, 0.8f, 1.2f);
            sync();
            return ItemInteractionResult.CONSUME;
        }

        // feeding a pair starts courtship
        BugSpecies pair = null;
        boolean anyEats = false;
        for (Resident r : residents) {
            if (r.data.species().food().test(stack)) {
                anyEats = true;
                long count = residents.stream().filter(o -> o.data.species() == r.data.species()).count();
                if (count >= 2) {
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
                if (!player.getInventory().add(s)) {
                    player.drop(s, false);
                }
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
        MutableComponent line = Component.empty();
        int soonest = Integer.MAX_VALUE;
        for (int i = 0; i < residents.size(); i++) {
            Resident r = residents.get(i);
            if (i > 0) line.append(", ");
            line.append(r.data.species().displayName().copy().withStyle(r.data.species().rarity().color));
            soonest = Math.min(soonest, r.timer);
        }
        line.append(Component.literal(" - ").withStyle(ChatFormatting.GRAY));
        if (breedTimer > 0) {
            line.append(Component.translatable("bugslife.msg.courting", StringUtil.formatTickDuration(breedTimer, 20f)).withStyle(ChatFormatting.LIGHT_PURPLE));
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
            if (bug == null) continue;
            bug.moveTo(worldPosition.getX() + 0.5, worldPosition.getY() + 0.1, worldPosition.getZ() + 0.5, level.random.nextFloat() * 360f, 0);
            bug.finalizeSpawn(server, server.getCurrentDifficultyAt(worldPosition), MobSpawnType.BUCKET, null);
            bug.setPrismatic(r.data.prismatic());
            if (r.data.species().movement() == Movement.HANG) bug.attachToCeiling();
            server.addFreshEntity(bug);
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

    private void writeBugs(CompoundTag tag) {
        ListTag list = new ListTag();
        for (Resident r : residents) {
            CompoundTag t = new CompoundTag();
            BugData.CODEC.encodeStart(NbtOps.INSTANCE, r.data).result().ifPresent(d -> t.put("Bug", d));
            t.putInt("Timer", r.timer);
            list.add(t);
        }
        tag.put("Bugs", list);
        tag.putInt("BreedTimer", breedTimer);
        if (breeding != null) tag.putString("Breeding", breeding.id());
    }

    private void readBugs(CompoundTag tag) {
        residents.clear();
        ListTag list = tag.getList("Bugs", Tag.TAG_COMPOUND);
        for (int i = 0; i < list.size(); i++) {
            CompoundTag t = list.getCompound(i);
            BugData.CODEC.parse(NbtOps.INSTANCE, t.get("Bug")).result()
                    .ifPresent(d -> residents.add(new Resident(d, t.getInt("Timer"))));
        }
        breedTimer = tag.getInt("BreedTimer");
        breeding = tag.contains("Breeding") ? BugSpecies.byId(tag.getString("Breeding")) : null;
        renderVersion++;
    }

    @Override
    protected void saveAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.saveAdditional(tag, registries);
        writeBugs(tag);
        tag.put("Output", output.serializeNBT(registries));
        if (breeder != null) tag.putUUID("Breeder", breeder);
    }

    @Override
    protected void loadAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.loadAdditional(tag, registries);
        readBugs(tag);
        if (tag.contains("Output")) output.deserializeNBT(registries, tag.getCompound("Output"));
        breeder = tag.hasUUID("Breeder") ? tag.getUUID("Breeder") : null;
    }

    @Override
    public CompoundTag getUpdateTag(HolderLookup.Provider registries) {
        CompoundTag tag = new CompoundTag();
        writeBugs(tag);
        return tag;
    }

    @Override
    public Packet<ClientGamePacketListener> getUpdatePacket() {
        return ClientboundBlockEntityDataPacket.create(this);
    }
}
