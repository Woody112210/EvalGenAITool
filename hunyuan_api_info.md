# Hunyuan API Information

## Model Path
- `fal-ai/hunyuan-image/v2.1/text-to-image`

## Required Parameters
- `prompt` (string, required): The text prompt to generate an image from

## Optional Parameters
- `negative_prompt` (string): Default ""
- `image_size` (ImageSizeEnum): Default "square_hd"
  - Options: square_hd, square, portrait_4_3, portrait_3_4, landscape_4_3, landscape_3_4, landscape_16_9, portrait_16_9
- `num_images` (integer): Default 1
- `num_inference_steps` (integer): Default 28
- `guidance_scale` (float): Default 3.5
- `seed` (integer): Random seed for reproducible results
- `use_reprompt` (boolean): Default true
- `use_refiner` (boolean): Enable refiner model for improved quality

## Example Usage
```javascript
const result = await fal.subscribe("fal-ai/hunyuan-image/v2.1/text-to-image", {
  input: {
    prompt: "A cute, cartoon-style anthropomorphic penguin plush toy, standing in a painting studio, wearing a red knitted scarf and beret."
  }
});
```

## Output Format
- `images`: List of generated images with URL
- `seed`: The base seed used for generation
