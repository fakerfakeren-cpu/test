package com.astralfall.block;

import com.astralfall.registry.ModParticles;
import com.astralfall.registry.ModSounds;
import com.astralfall.util.FX;
import com.mojang.serialization.MapCodec;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundSource;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.phys.Vec3;

/** Trap: anything that steps on the rune is flung into the air. Sneaking lets you cross safely. */
public class GravityRuneBlock extends Block {
    public static final MapCodec<GravityRuneBlock> CODEC = simpleCodec(GravityRuneBlock::new);
    public static final BooleanProperty ACTIVE = BooleanProperty.create("active");

    public GravityRuneBlock(Properties props) {
        super(props);
        registerDefaultState(stateDefinition.any().setValue(ACTIVE, false));
    }

    @Override
    protected MapCodec<? extends Block> codec() {
        return CODEC;
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(ACTIVE);
    }

    @Override
    public void stepOn(Level level, BlockPos pos, BlockState state, Entity entity) {
        if (!(level instanceof ServerLevel server) || state.getValue(ACTIVE)) return;
        if (!(entity instanceof LivingEntity) || entity.isShiftKeyDown()) return;
        entity.setDeltaMovement(entity.getDeltaMovement().x * 0.5, 1.45, entity.getDeltaMovement().z * 0.5);
        entity.hurtMarked = true;
        entity.resetFallDistance();
        server.setBlock(pos, state.setValue(ACTIVE, true), 3);
        server.scheduleTick(pos, this, 30);
        Vec3 c = Vec3.atCenterOf(pos).add(0, 0.6, 0);
        FX.ring(server, ModParticles.VOID_MOTE.get(), c, 0.8, 16, 0.4);
        FX.burst(server, ParticleTypes.REVERSE_PORTAL, c, 30, 0.3, 0.3);
        server.playSound(null, pos, ModSounds.GRAVITY_THROW.get(), SoundSource.BLOCKS, 1.0f, 1.3f);
    }

    @Override
    protected void tick(BlockState state, ServerLevel level, BlockPos pos, RandomSource random) {
        if (state.getValue(ACTIVE)) level.setBlock(pos, state.setValue(ACTIVE, false), 3);
    }

    @Override
    public void animateTick(BlockState state, Level level, BlockPos pos, RandomSource random) {
        if (random.nextInt(5) == 0) {
            level.addParticle(ParticleTypes.REVERSE_PORTAL, pos.getX() + random.nextDouble(), pos.getY() + 1.05, pos.getZ() + random.nextDouble(), 0, 0.05, 0);
        }
    }
}
