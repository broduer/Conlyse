export function pushDrawing(drawings, drawingLevel, fillColor, outlineColor, strokeWidth, data){
    let dw_copy = [...drawings]
    let drawing = {
        "drawingLevel": drawingLevel,
        "fillColor": fillColor,
        "outlineColor": outlineColor,
        "strokeWidth": strokeWidth,
        "data": data
    }
    dw_copy.push(drawing)
    return dw_copy
}