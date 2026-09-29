package com.bugslife.block;

import com.bugslife.registry.ModBlockEntities;
import com.mojang.serialization.MapCodec;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.ItemInteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.BaseEntityBlock;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.jetbrains.annotations.Nullable;

import java.util.List;

/**
 * A glass box for keeping bugs. Holds up to four; they produce harvests over time, breed when a pair is fed,
 * and light the terrarium if they glow. Hoppers can pull the harvest out.
 */
public class TerrariumBlock extends BaseEntityBlock {
    public static final MapCodec<TerrariumBlock> CODEC = simpleCodec(TerrariumBlock::new);
    public static final IntegerProperty LIGHT = IntegerProperty.create("light", 0, 15);
    private static final VoxelShape SHAPE = Block.box(0.5, 0, 0.5, 15.5, 15, 15.5);

    /** How many bugs fit inside. */
    public final int capacity;
    /** Harvest speed multiplier. */
    public final float speed;

    public TerrariumBlock(Properties properties) {
        this(properties, 4, 1.0f);
    }

    public TerrariumBlock(Properties properties, int capacity, float speed) {
        super(properties);
        this.capacity = capacity;
        this.speed = speed;
        registerDefaultState(stateDefinition.any().setValue(LIGHT, 0));
    }

    @Override
    protected MapCodec<? extends BaseEntityBlock> codec() {
        return CODEC;
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(LIGHT);
    }

    @Override
    protected RenderShape getRenderShape(BlockState state) {
        return RenderShape.MODEL;
    }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return SHAPE;
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new TerrariumBlockEntity(pos, state);
    }

    @Nullable
    @Override
    public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level level, BlockState state, BlockEntityType<T> type) {
        return level.isClientSide ? null : createTickerHelper(type, ModBlockEntities.TERRARIUM.get(), TerrariumBlockEntity::serverTick);
    }

    @Override
    protected ItemInteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos, Player player,
                                              InteractionHand hand, BlockHitResult hit) {
        if (level.getBlockEntity(pos) instanceof TerrariumBlockEntity be) {
            return be.useItem(stack, player, hand);
        }
        return ItemInteractionResult.PASS_TO_DEFAULT_BLOCK_INTERACTION;
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (level.getBlockEntity(pos) instanceof TerrariumBlockEntity be) {
            return be.collect(player);
        }
        return InteractionResult.PASS;
    }

    @Override
    protected void onRemove(BlockState state, Level level, BlockPos pos, BlockState newState, boolean movedByPiston) {
        if (!state.is(newState.getBlock()) && level.getBlockEntity(pos) instanceof TerrariumBlockEntity be) {
            be.releaseAll();
        }
        super.onRemove(state, level, pos, newState, movedByPiston);
    }

    @Override
    protected boolean hasAnalogOutputSignal(BlockState state) {
        return true;
    }

    @Override
    protected int getAnalogOutputSignal(BlockState state, Level level, BlockPos pos) {
        return level.getBlockEntity(pos) instanceof TerrariumBlockEntity be ? be.bugCount() * 15 / Math.max(1, be.capacity()) : 0;
    }

    @Override
    public void appendHoverText(ItemStack stack, Item.TooltipContext context, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.translatable("block.bugslife.terrarium.tip1", capacity).withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable("block.bugslife.terrarium.tip2").withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.translatable("block.bugslife.terrarium.tip3").withStyle(ChatFormatting.GRAY));
        if (speed > 1.0f) {
            tooltip.add(Component.translatable("block.bugslife.terrarium.speed", Math.round((speed - 1.0f) * 100)).withStyle(ChatFormatting.BLUE));
        }
    }
}
