{% load static %}<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h2, h3 { text-align: center; margin: 5px 0; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #333; padding: 8px; text-align: left; font-size: 11px; }
        th { background-color: #2196F3; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        .fecha { text-align: center; margin-top: 10px; font-size: 10px; color: #666; }
        .precio { text-align: right; }
    </style>
</head>
<body>
    <h2>OKSU MODA</h2>
    <h3>${titulo}</h3>
    <p class="fecha">Generado el: ${.now?string["dd/MM/yyyy HH:mm"]}</p>
    
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Nombre</th>
                <th>Descripción</th>
                <th>Precio</th>
                <th>Stock</th>
                <th>Estado</th>
            </tr>
        </thead>
        <tbody>
            <#list productos as producto>
            <tr>
                <td>${producto.id}</td>
                <td>${producto.nombre}</td>
                <td>${producto.descripcion!""}</td>
                <td class="precio">$${producto.precio?string["#,###.00"]}</td>
                <td>${producto.stock}</td>
                <td>${producto.estado}</td>
            </tr>
            </#list>
        </tbody>
    </table>
    
    <p class="fecha">Total de registros: ${productos?size}</p>
</body>
</html>