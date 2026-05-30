{% load static %}<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h2, h3 { text-align: center; margin: 5px 0; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #333; padding: 8px; text-align: left; font-size: 11px; }
        th { background-color: #9C27B0; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        .fecha { text-align: center; margin-top: 10px; font-size: 10px; color: #666; }
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
                <th>Email</th>
                <th>Teléfono</th>
                <th>Estado</th>
            </tr>
        </thead>
        <tbody>
            <#list clientes as cliente>
            <tr>
                <td>${cliente.idCliente}</td>
                <td>${cliente.nombre}</td>
                <td>${cliente.email!""}</td>
                <td>${cliente.telefono!""}</td>
                <td>${cliente.estado}</td>
            </tr>
            </#list>
        </tbody>
    </table>
    
    <p class="fecha">Total de registros: ${clientes?size}</p>
</body>
</html>