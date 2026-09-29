package com.oathbound.block;

import com.mojang.serialization.MapCodec;
import com.oathbound.registry.ModBlocks;
import com.oathbound.registry.ModItems;
import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import com.oathbound.util.Vfx;
import com.oathbound.util.Puzzles;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;

import java.util.List;

/**
 * A numbered stone dial in the Arcanist's Spire. Its face turns through six glyphs: Sun, Moon, Flame, Tide,
 * Crown and Eye. Set dials I to IV to the answers of the Cipher's riddles to dissolve the Archmage's ward.
 * The dials will not turn for anyone who has not borne the Seal of Valor.
 */
public class RuneDialBlock extends HorizontalDirectionalBlock {
    public static final MapCodec<RuneDialBlock> CODEC = simpleCodec(RuneDialBlock::new);
    public static final IntegerProperty GLYPH = IntegerProperty.create("glyph", 0, 5);
    public static final IntegerProperty NUMBER = IntegerProperty.create("number", 0, 3);
    public static final int GLYPHS = 6;
    public static final String[] NUMERALS = {"I", "II", "III", "IV"};

    public RuneDialBlock(Properties props) {
        super(props);
        registerDefaultState(stateDefinition.any().setValue(FACING, net.minecraft.core.Direction.NORTH).setValue(GLYPH, 0).setValue(NUMBER, 0));
    }

    @Override
    protected MapCodec<? extends HorizontalDirectionalBlock> codec() {
        return CODEC;
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(FACING, GLYPH, NUMBER);
    }

    @Override
    public BlockState getStateForPlacement(BlockPlaceContext ctx) {
        return defaultBlockState().setValue(FACING, ctx.getHorizontalDirection().getOpposite());
    }

    public static Component glyphName(int glyph) {
        return Component.translatable("glyph.oathbound." + glyph).withStyle(ChatFormatting.LIGHT_PURPLE, ChatFormatting.BOLD);
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (!(level instanceof ServerLevel server)) return InteractionResult.SUCCESS;
        List<BlockPos> lecterns = Puzzles.find(server, pos, 12, ModBlocks.CIPHER_LECTERN.get());
        if (!lecterns.isEmpty() && server.getBlockState(lecterns.get(0)).getValue(CipherLecternBlock.SOLVED)) {
            player.sendOverlayMessage(Component.translatable("message.oathbound.dial.locked").withStyle(ChatFormatting.GRAY));
            return InteractionResult.SUCCESS;
        }
        if (!Puzzles.has(player, ModItems.SEAL_OF_VALOR.get())) {
            player.sendOverlayMessage(Component.translatable("message.oathbound.dial.valor").withStyle(ChatFormatting.RED));
            server.playSound(null, pos, ModSounds.DIAL_TURN.get(), SoundSource.BLOCKS, 0.5f, 0.5f);
            return InteractionResult.SUCCESS;
        }
        int dir = player.isShiftKeyDown() ? GLYPHS - 1 : 1;
        int glyph = (state.getValue(GLYPH) + dir) % GLYPHS;
        server.setBlock(pos, state.setValue(GLYPH, glyph), 3);
        server.playSound(null, pos, ModSounds.DIAL_TURN.get(), SoundSource.BLOCKS, 1.0f, 0.9f + glyph * 0.05f);
        var f = state.getValue(FACING);
        Vfx.burst(server, ModParticles.ARCANE_GLYPH.get(), Vec3.atCenterOf(pos).add(f.getStepX() * 0.6, 0, f.getStepZ() * 0.6), 6, 0.2, 0.02);
        player.sendOverlayMessage(Component.translatable("message.oathbound.dial.shows", NUMERALS[state.getValue(NUMBER)], glyphName(glyph)).withStyle(ChatFormatting.GRAY));
        if (!lecterns.isEmpty()) CipherLecternBlock.check(server, lecterns.get(0), player);
        return InteractionResult.SUCCESS;
    }
}
