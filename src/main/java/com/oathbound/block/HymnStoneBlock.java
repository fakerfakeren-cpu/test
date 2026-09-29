package com.oathbound.block;

import com.oathbound.entity.SpellMarkEntity;
import com.mojang.serialization.MapCodec;
import com.oathbound.quest.QuestLog;
import com.oathbound.registry.ModBlocks;
import com.oathbound.registry.ModParticles;
import com.oathbound.registry.ModSounds;
import com.oathbound.util.Vfx;
import com.oathbound.util.Puzzles;
import com.oathbound.util.Scheduler;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.EntitySpawnReason;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;

import java.util.HashMap;
import java.util.Map;

/**
 * The Hymn Stone of a Drowned Chapel. It answers only a Warden's light: read it with a lit lantern to hear
 * and see the Hymn of the Tide (five notes, different in every chapel), then ring the chapel bells in that
 * order. A wrong note resets the hymn and stirs the drowned. The right hymn lifts the crypt grate.
 */
public class HymnStoneBlock extends Block {
    public static final MapCodec<HymnStoneBlock> CODEC = simpleCodec(HymnStoneBlock::new);
    public static final IntegerProperty PROGRESS = IntegerProperty.create("progress", 0, 5);
    public static final BooleanProperty SOLVED = BooleanProperty.create("solved");
    public static final int LENGTH = 5;
    private static final Map<Long, Long> DISCORD_COOLDOWN = new HashMap<>();

    public HymnStoneBlock(Properties props) {
        super(props);
        registerDefaultState(stateDefinition.any().setValue(PROGRESS, 0).setValue(SOLVED, false));
    }

    @Override
    protected MapCodec<? extends Block> codec() {
        return CODEC;
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(PROGRESS, SOLVED);
    }

    /** The hymn for the chapel whose stone sits at {@code pos}: five tones, never the same note twice in a row. */
    public static int[] hymn(BlockPos pos) {
        int k = Puzzles.key(pos);
        int[] out = new int[LENGTH];
        int prev = -1;
        for (int i = 0; i < LENGTH; i++) {
            int t = (k >>> (i * 3)) & 3;
            if (t == prev) t = (t + 1 + ((k >>> 20) & 1)) & 3;
            out[i] = t;
            prev = t;
        }
        return out;
    }

    public static MutableComponent hymnText(int[] hymn) {
        MutableComponent c = Component.empty();
        for (int i = 0; i < hymn.length; i++) {
            if (i > 0) c.append(Component.literal("  →  ").withStyle(ChatFormatting.DARK_GRAY));
            c.append(ChapelBellBlock.toneName(hymn[i]));
        }
        return c;
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos, Player player, BlockHitResult hit) {
        if (!(level instanceof ServerLevel server)) return InteractionResult.SUCCESS;
        if (state.getValue(SOLVED)) {
            player.sendOverlayMessage(Component.translatable("message.oathbound.hymn.solved").withStyle(ChatFormatting.AQUA));
            return InteractionResult.SUCCESS;
        }
        if (!Puzzles.hasLitLantern(player)) {
            player.sendSystemMessage(Component.translatable("message.oathbound.hymn.cold").withStyle(ChatFormatting.GRAY, ChatFormatting.ITALIC));
            server.playSound(null, pos, ModSounds.BELL_WRONG.get(), SoundSource.BLOCKS, 0.4f, 0.5f);
            return InteractionResult.SUCCESS;
        }
        int[] hymn = hymn(pos);
        player.sendSystemMessage(Component.literal(""));
        player.sendSystemMessage(Component.translatable("message.oathbound.hymn.title").withStyle(ChatFormatting.DARK_AQUA, ChatFormatting.BOLD));
        player.sendSystemMessage(Component.translatable("message.oathbound.hymn.verse").withStyle(ChatFormatting.GRAY, ChatFormatting.ITALIC));
        player.sendSystemMessage(hymnText(hymn));
        player.sendSystemMessage(Component.translatable("message.oathbound.hymn.instructions").withStyle(ChatFormatting.GRAY));
        // The stone hums the melody itself.
        for (int i = 0; i < hymn.length; i++) {
            int tone = hymn[i];
            Scheduler.later(server, 10 + i * 14, l -> {
                l.playSound(null, pos, ModSounds.bell(tone), SoundSource.BLOCKS, 1.0f, 1.0f);
                Vfx.burst(l, ModParticles.TIDE.get(), Vec3.atCenterOf(pos).add(0, 0.7, 0), 8, 0.3, 0.03);
            });
        }
        if (state.getValue(PROGRESS) != 0) server.setBlock(pos, state.setValue(PROGRESS, 0), 3);
        return InteractionResult.SUCCESS;
    }

    public static void onBellRung(ServerLevel level, BlockPos stonePos, int tone, Player player) {
        BlockState state = level.getBlockState(stonePos);
        if (!state.is(ModBlocks.HYMN_STONE.get()) || state.getValue(SOLVED)) return;
        if (!Puzzles.hasLitLantern(player)) {
            player.sendOverlayMessage(Component.translatable("message.oathbound.hymn.cold_short").withStyle(ChatFormatting.GRAY));
            return;
        }
        int[] hymn = hymn(stonePos);
        int progress = state.getValue(PROGRESS);
        if (hymn[progress] == tone) {
            progress++;
            Vfx.burst(level, ModParticles.TIDE.get(), Vec3.atCenterOf(stonePos).add(0, 0.8, 0), 12 + progress * 4, 0.4, 0.05);
            if (progress >= LENGTH) {
                solve(level, stonePos, player);
            } else {
                level.setBlock(stonePos, state.setValue(PROGRESS, progress), 3);
                player.sendOverlayMessage(Component.translatable("message.oathbound.hymn.progress", progress, LENGTH).withStyle(ChatFormatting.AQUA));
            }
        } else {
            level.setBlock(stonePos, state.setValue(PROGRESS, 0), 3);
            level.playSound(null, stonePos, ModSounds.BELL_WRONG.get(), SoundSource.BLOCKS, 2.0f, 1.0f);
            player.sendSystemMessage(Component.translatable("message.oathbound.hymn.discord").withStyle(ChatFormatting.DARK_RED, ChatFormatting.ITALIC));
            long now = level.getGameTime();
            Long last = DISCORD_COOLDOWN.get(stonePos.asLong());
            if (last == null || now - last > 200) {
                DISCORD_COOLDOWN.put(stonePos.asLong(), now);
                stirDrowned(level, player);
            }
        }
    }

    private static void stirDrowned(ServerLevel level, Player player) {
        RandomSource r = level.getRandom();
        for (int i = 0; i < 2; i++) {
            Mob m = net.minecraft.world.entity.EntityTypes.DROWNED.create(level, EntitySpawnReason.EVENT);
            if (m == null) continue;
            double a = r.nextDouble() * Math.PI * 2;
            BlockPos at = BlockPos.containing(player.getX() + Math.cos(a) * 5, player.getY(), player.getZ() + Math.sin(a) * 5);
            for (int dy = 0; dy < 4 && !level.getBlockState(at).isAir() && !level.getBlockState(at).liquid(); dy++) at = at.above();
            m.snapTo(at.getX() + 0.5, at.getY(), at.getZ() + 0.5, r.nextFloat() * 360, 0);
            m.setTarget(player);
            level.addFreshEntity(m);
            Vfx.burst(level, net.minecraft.core.particles.ParticleTypes.SPLASH, m.position().add(0, 1, 0), 30, 0.5, 0.2);
        }
    }

    public static void solve(ServerLevel level, BlockPos pos, Player player) {
        BlockState state = level.getBlockState(pos);
        level.setBlock(pos, state.setValue(SOLVED, true).setValue(PROGRESS, 0), 3);
        level.playSound(null, pos, ModSounds.PUZZLE_SOLVED.get(), SoundSource.BLOCKS, 2.5f, 1.0f);
        Vec3 c = Vec3.atCenterOf(pos);
        Vfx.sphere(level, ModParticles.TIDE.get(), c, 3, 90);
        Vfx.ring(level, ModParticles.LUMEN_MOTE.get(), c, 5, 60, 0.1);
        SpellMarkEntity.sigil(level, Vec3.atBottomCenterOf(pos), 3f, SpellMarkEntity.Hue.TIDE, 80);
        SpellMarkEntity.ring(level, Vec3.atBottomCenterOf(pos), 10f, SpellMarkEntity.Hue.TIDE, 24);
        SpellMarkEntity.pillar(level, Vec3.atBottomCenterOf(pos), 0.7f, SpellMarkEntity.Hue.TIDE, 40);
        int[] hymn = hymn(pos);
        for (int i = 0; i < hymn.length; i++) {
            int tone = hymn[i];
            Scheduler.later(level, 6 + i * 5, l -> l.playSound(null, pos, ModSounds.bell(tone), SoundSource.BLOCKS, 1.4f, 1.0f));
        }
        Puzzles.unseal(level, pos, 20, ModBlocks.SEALED_GRATE.get(), ModParticles.TIDE.get(), ModSounds.WARD_DISSOLVE.get());
        if (player != null) {
            player.sendSystemMessage(Component.translatable("message.oathbound.hymn.opened").withStyle(ChatFormatting.AQUA, ChatFormatting.ITALIC));
            if (player instanceof ServerPlayer sp) QuestLog.grant(sp, "hymn", "solved");
        }
    }
}
