using Godot;

// Programmatic 2D blockout; replace with properly layered sprites later.
public partial class SukiPlaceholder : Node2D
{
    private float elapsed;
    public override void _Process(double delta) { elapsed += (float)delta; QueueRedraw(); }
    public override void _Draw()
    {
        Vector2 c = GetViewportRect().Size / 2;
        DrawCircle(c + new Vector2(0, 45), 85, new Color("f6f0e6")); // rice
        DrawEllipse(c + new Vector2(0, -10), new Vector2(116, 77), new Color("fa885c"));
        DrawLine(c + new Vector2(-5, -87), c + new Vector2(13, -13), new Color("a4c65a"), 22); // avocado fringe
        DrawCircle(c + new Vector2(-4, -98), 22, new Color("296f35")); // jalapeno
        DrawCircle(c + new Vector2(-4, -98), 9, new Color("e83d27")); // sauce
        foreach (int x in new[] { -33, 32 })
        {
            DrawCircle(c + new Vector2(x, 1), 14, new Color("fdfdfd"));
            DrawCircle(c + new Vector2(x, 1), 9, new Color("4b9a48"));
            DrawCircle(c + new Vector2(x, 1), 4, new Color("152b17"));
        }
        DrawArc(c + new Vector2(0, 30), 15, 0, Mathf.Pi, 24, new Color("672d28"), 3);
        float wave = Mathf.Sin(elapsed * 4) * 15;
        DrawLine(c + new Vector2(-91, 45), c + new Vector2(-135, 70), new Color("1d2b20"), 12);
        DrawLine(c + new Vector2(91, 45), c + new Vector2(135, 35 + wave), new Color("1d2b20"), 12);
        DrawLine(c + new Vector2(-35, 116), c + new Vector2(-43, 168), new Color("1d2b20"), 15);
        DrawLine(c + new Vector2(35, 116), c + new Vector2(43, 168), new Color("1d2b20"), 15);
    }
    private void DrawEllipse(Vector2 center, Vector2 radius, Color color)
    {
        var points = new Vector2[65];
        for (int i = 0; i < points.Length; i++)
        {
            float a = i * Mathf.Tau / (points.Length - 1);
            points[i] = center + new Vector2(Mathf.Cos(a) * radius.X, Mathf.Sin(a) * radius.Y);
        }
        DrawColoredPolygon(points, color);
    }
}
