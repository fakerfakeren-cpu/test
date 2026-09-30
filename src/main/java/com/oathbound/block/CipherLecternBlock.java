package com.oathbound.block;

import com.oathbound.entity.SpellMarkEntity;
import com.mojang.serialization.MapCodec;
import com.oathbound.quest.QuestLog;
import com.oathbound.registry.ModBlocks;
import com.oathbound.registry.ModItems;
import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import com.oathbound.util.Vfx;
import com.oathbound.util.Puzzles;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.HorizontalDirectionalBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.Shapes;
import net.minecraft.world.phys.shapes.VoxelShape;

import java.util.ArrayList;
import java.util.List;

/**
 * The Archmage's Cipher. Its four riddles (different in every spire) name four glyphs; set the numbered
 * Rune Dials to match and the ward before Veyl's sanctum dissolves.
 */
public class CipherLecternBlock extends HorizontalDirectionalBlock {
    public static final MapCodec<CipherLecternBlock> CODEC = simpleCodec(CipherLecternBlock::new);
    public static final BooleanProperty SOLVED = BooleanProperty.create("solved");
    private static final VoxelShape SHAPE = Shapes.or(Block.box(4, 0, 4, 12, 2, 12), Block.box(6, 2, 6, 10, 12, 10), Block.box(1, 12, 1, 15, 15, 15));

    public CipherLecternBlock(Properties props) {
        super(props);
        registerDefaultState(stateDefinition.any().setValue(FACING, net.minecraft.core.Direction.NORTH).setValue(SOLVED, false));
    }

    @Override
    protected MapCodec<? extends HorizontalDirectionalBlock> codec() {
        return CODEC;
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(FACING, SOLVED);
    }

    @Override
    public BlockState getStateForPlacement(BlockPlaceContext ctx) {
        return defaultBlockState().setValue(FACING, ctx.getHorizontalDirection().getOpposite());
    }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext ctx) {
        return SHAPE;
    }

    /** The four answer glyphs for this spire (all different). */
    public static int[] answer(BlockPos pos) {
        int k = Puzzles.key(pos);
        List<Integer> pool = new ArrayList<>(List.of(0, 1, 2, 3, 4, 5));
        int[] out = new int[4];
        for (int i = 0; i < 4; i++) {
            int idx = (k >>> (i * 5)) % pool.size();
            out[i] = pool.remove(idx);
        }
        return out;
    }

    /** Which of the two riddles for each glyph this spire uses. */
    private static int variant(BlockPos pos, int i) {
        return (Puzzles.key(pos) >>> (22 + i)) & 1;
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (!(level instanceof ServerLevel server)) return InteractionResult.SUCCESS;
        if (state.getValue(SOLVED)) {
            player.sendOverlayMessage(Component.translatable("message.oathbound.cipher.solved").withStyle(ChatFormatting.LIGHT_PURPLE));
            return InteractionResult.SUCCESS;
        }
        if (!Puzzles.has(player, ModItems.SEAL_OF_VALOR.get())) {
            player.sendSystemMessage(Component.translatable("message.oathbound.cipher.dark").withStyle(ChatFormatting.GRAY, ChatFormatting.ITALIC));
            return InteractionResult.SUCCESS;
        }
        int[] ans = answer(pos);
        server.playSound(null, pos, ModSounds.CHRONICLE_PAGE.get(), SoundSource.BLOCKS, 1.0f, 0.7f);
        player.sendSystemMessage(Component.literal(""));
        player.sendSystemMessage(Component.translatable("message.oathbound.cipher.title").withStyle(ChatFormatting.LIGHT_PURPLE, ChatFormatting.BOLD));
        for (int i = 0; i < 4; i++) {
            player.sendSystemMessage(Component.literal(RuneDialBlock.NUMERALS[i] + ". ").withStyle(ChatFormatting.DARK_PURPLE, ChatFormatting.BOLD)
                .append(Component.translatable("riddle.oathbound." + ans[i] + "." + variant(pos, i)).withStyle(ChatFormatting.GRAY, ChatFormatting.ITALIC)));
        }
        MutableComponent glyphs = Component.empty();
        for (int g = 0; g < RuneDialBlock.GLYPHS; g++) {
            if (g > 0) glyphs.append(Component.literal(" \u00b7 ").withStyle(ChatFormatting.DARK_GRAY));
            glyphs.append(RuneDialBlock.glyphName(g));
        }
        player.sendSystemMessage(Component.translatable("message.oathbound.cipher.glyphs", glyphs).withStyle(ChatFormatting.GRAY));
        player.sendSystemMessage(Component.translatable("message.oathbound.cipher.instructions").withStyle(ChatFormatting.DARK_GRAY));
        Vfx.burst(server, ModParticles.ARCANE_GLYPH.get(), Vec3.atCenterOf(pos).add(0, 0.8, 0), 20, 0.4, 0.03);
        return InteractionResult.SUCCESS;
    }

    public static boolean check(ServerLevel level, BlockPos pos, Player player) {
        BlockState state = level.getBlockState(pos);
        if (!state.is(ModBlocks.CIPHER_LECTERN.get()) || state.getValue(SOLVED)) return false;
        int[] ans = answer(pos);
        int[] set = {-1, -1, -1, -1};
        for (BlockPos p : Puzzles.find(level, pos, 12, ModBlocks.RUNE_DIAL.get())) {
            BlockState d = level.getBlockState(p);
            set[d.getValue(RuneDialBlock.NUMBER)] = d.getValue(RuneDialBlock.GLYPH);
        }
        for (int i = 0; i < 4; i++) if (set[i] != ans[i]) return false;
        solve(level, pos, player);
        return true;
    }

    public static void solve(ServerLevel level, BlockPos pos, Player player) {
        level.setBlock(pos, level.getBlockState(pos).setValue(SOLVED, true), 3);
        level.playSound(null, pos, ModSounds.PUZZLE_SOLVED.get(), SoundSource.BLOCKS, 2.5f, 1.15f);
        Vfx.sphere(level, ModParticles.ARCANE_GLYPH.get(), Vec3.atCenterOf(pos), 3, 100);
        SpellMarkEntity.sigil(level, Vec3.atBottomCenterOf(pos), 3.2f, SpellMarkEntity.Hue.ARCANE, 80);
        SpellMarkEntity.ring(level, Vec3.atBottomCenterOf(pos), 12f, SpellMarkEntity.Hue.ARCANE, 26);
        SpellMarkEntity.halo(level, Vec3.atCenterOf(pos).add(0, 1.2, 0), 1.2f, SpellMarkEntity.Hue.ARCANE, 80);
        Puzzles.unseal(level, pos, 24, ModBlocks.ARCANE_WARD.get(), ModParticles.ARCANE_GLYPH.get(), ModSounds.WARD_DISSOLVE.get());
        if (player != null) {
            player.sendSystemMessage(Component.translatable("message.oathbound.cipher.opened").withStyle(ChatFormatting.LIGHT_PURPLE, ChatFormatting.ITALIC));
            if (player instanceof ServerPlayer sp) QuestLog.grant(sp, "cipher", "solved");
        }
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        if (random.nextInt(3) != 0) return;
        level.addParticle(ModParticles.ARCANE_GLYPH.get(), pos.getX() + 0.2 + random.nextDouble() * 0.6, pos.getY() + 1.1 + random.nextDouble() * 0.4,
            pos.getZ() + 0.2 + random.nextDouble() * 0.6, 0, 0.02, 0);
    }
}
