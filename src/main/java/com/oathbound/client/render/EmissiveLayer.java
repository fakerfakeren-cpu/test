package com.oathbound.client.render;

import net.minecraft.client.model.EntityModel;
import net.minecraft.client.renderer.entity.RenderLayerParent;
import net.minecraft.client.renderer.entity.layers.EyesLayer;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.resources.Identifier;

/** Draws a creature's "_glow" texture unlit, so eyes, runes and embers shine in the dark. */
public class EmissiveLayer<S extends EntityRenderState, M extends EntityModel<S>> extends EyesLayer<S, M> {
    private final RenderType glow;

    public EmissiveLayer(RenderLayerParent<S, M> parent, Identifier texture) {
        super(parent);
        this.glow = RenderTypes.eyes(texture);
    }

    @Override
    public RenderType renderType() {
        return glow;
    }
}
