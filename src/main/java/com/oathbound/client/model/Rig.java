package com.oathbound.client.model;

import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.entity.state.EntityRenderState;

/**
 * Base for Oathbound models: every creature hangs from a "hull" part so whole-body poses are one rotation.
 * Parts are looked up by name through the paths {@link ModelDefs} records for each model.
 */
public abstract class Rig<S extends EntityRenderState> extends EntityModel<S> {
    protected final ModelPart hull;
    private final String model;

    protected Rig(ModelPart root, String model) {
        super(root);
        this.model = model;
        this.hull = root.getChild("hull");
    }

    /** The named part, or null if this model has none (for rigs shared by several body plans). */
    protected ModelPart opt(String name) {
        return ModelDefs.path(model, name) == null ? null : part(name);
    }

    protected ModelPart part(String name) {
        String[] path = ModelDefs.path(model, name);
        if (path == null) throw new IllegalArgumentException(model + " has no part " + name);
        ModelPart p = root();
        for (String step : path) p = p.getChild(step);
        return p;
    }
}
